# Trend Test 

## Why do we need this?

This test quantifies the probability that the observed trend has arisen by chance. By permuting the data, we simulate random scenarios and compare our observed trends with the trends from the simulations.

## How does it work?

**Observations and Metrics**

+ **Trend:** First, we calculate slope on the raw data, which represents the observed magnitude and direction of the change. 

+ **Aggregated $R^2$:** We calculate $R^2$ to provide a measure of the trend's reliability. By taking the mean value for each time point, we filter out individual level noise to reveal the general direction of the group.

+ **$R^2$:** We also retain the $R^2$ calculated on the raw data. While usually low, this metric indicates how much individual behaviour varies around the general trend. 

```sql
WITH filtered_data AS (
    SELECT
        {group_col},             
        {range_col},
        {value_col}
    FROM
        _data
    WHERE
        {range_col} BETWEEN {range_start} AND {range_end}
    ORDER BY
        {range_col}
),

observed_r2 AS (
    SELECT 
        {group_col},
        REGR_R2(mean, {range_col}) as r_squared_mean
    FROM(
        SELECT
            {group_col},
            {range_col},
            AVG({value_col}) as mean
        FROM
            filtered_data
        GROUP BY
            1, 2    
        )
    GROUP BY
        1
),

observed_trend AS (
    SELECT 
        {group_col},
        REGR_SLOPE({value_col}, {range_col}) as obs_trend,
        REGR_R2({value_col}, {range_col}) as r_squared
    FROM 
        filtered_data
    GROUP BY
        1
),

```

**Creating Simulation Table**

+ To estimate the probability of observing such a trend by chance, we generate `n_iterations` of random datasets. We use `CROSS JOIN` with `EXPLODE` to replicate dataset.

```sql
iterations AS (
    SELECT 
        {range_col},
        {group_col},
        {value_col}, 
        iteration
    FROM
        filtered_data
    CROSS JOIN 
        (SELECT EXPLODE(SEQUENCE(1, {n_iterations})) AS iteration)
),

```

+ The core of the permutation test is to eliminate relationship between time and value.

+ We keep the time column (`range_col`) ordered. Then, we randomize the `value_col` using `ROW_NUMBER() OVER (PARTITION BY iteration, {group_col} ORDER BY rand())` for each iteration.

+ Finally, we join the randomized values to the fixed time points using the condition: `ON a.iteration = b.iteration AND
       a.{group_col} = b.{group_col} AND
       a.rn = b.random_rn`.

+ Note that `b.{value_col}` represents the randomized values.

```sql

shuffled_data AS (
    SELECT
        a.iteration,
        a.{group_col},
        a.{range_col},
        b.{value_col} 
    FROM
        (
        SELECT 
            *, 
            ROW_NUMBER() OVER (PARTITION BY iteration, {group_col} ORDER BY {range_col}) AS rn
        FROM 
            iterations
        ) a
    JOIN
        (
        SELECT 
            *, 
            ROW_NUMBER() OVER (PARTITION BY iteration, {group_col} ORDER BY rand()) AS random_rn
        FROM 
            iterations
        ) b
    ON a.iteration = b.iteration AND
    a.{group_col} = b.{group_col} AND
    a.rn = b.random_rn
),

```

**Final Part - Simulation and P-Value Calculation:**

+ For every simulated scenario (iteration), we calculate the slope of the shuffled data.

+ Finally, we determine the P-Value by calculating the proportion of random scenarios that produced a trend more extreme than our observed trend.

+ **For Positive Trend:** How often did random noise produce a steeper incline?

+ **For Negative Trend:** How often did random noise produce a steeper decline?

+ Low p-value indicates that the observed trend is unlikely to be observed by chance

```sql
perm_trends AS (
    SELECT
        iteration,
        {group_col},
        REGR_SLOPE({value_col}, {range_col}) as perm_trend
    FROM
        shuffled_data
    GROUP BY
        1,2
)

SELECT 
    t.{group_col},
    t.obs_trend,
    t.r_squared,
    r.r_squared_mean,
    AVG(
        CASE 
            WHEN t.obs_trend > 0 AND p.perm_trend >= t.obs_trend THEN 1
            WHEN t.obs_trend < 0 AND p.perm_trend <= t.obs_trend THEN 1
            ELSE 0
        END
    ) AS p_value,
    {n_iterations} AS n_iterations
FROM 
    perm_trends p
JOIN 
    observed_trend t ON p.{group_col} = t.{group_col}
JOIN 
    observed_r2 r ON p.{group_col} = r.{group_col}
GROUP BY 
    1,2,3,4
```
