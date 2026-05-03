# Trend Test

## Why do we need this?

Imagine you're tracking monthly water consumption across different districts, or monitoring weekly sales performance. You notice that one district's consumption is steadily increasing—but is this a **real trend** or just **random noise**?

This test answers that question by quantifying the probability that the observed trend could have arisen by pure chance. The key idea: if there's no real trend, then shuffling the time order of your data shouldn't make things much worse. If shuffling destroys a strong pattern, you've found something real.

## The Core Concept: Breaking the Time Connection

**The Logic**: If a trend is real, the sequence matters. Water consumption in January → February → March follows a pattern. But if there's no trend, then January's value could just as easily have occurred in March—it's all random fluctuation.

**The Test**:
1. Calculate the slope (trend) in your actual data
2. Shuffle the values across time points thousands of times
3. Calculate the slope in each shuffled version
4. Ask: "How often did random shuffling produce a trend as strong as the real one?"

If random shuffling rarely produces such a strong trend, you've confirmed it's **statistically significant**.

## A Simple Example

**Scenario**: You're analyzing monthly ice cream sales (in thousands) over 6 months:

| Month | Sales |
|-------|-------|
| Jan   | 10    |
| Feb   | 12    |
| Mar   | 15    |
| Apr   | 18    |
| May   | 21    |
| Jun   | 23    |

**Observed slope**: +2.6 (sales increase by ~2,600 units per month)

**The Test**: We shuffle the sales values randomly:
- One shuffle: [23, 10, 15, 21, 12, 18] → slope = +0.4
- Another: [15, 18, 10, 23, 12, 21] → slope = +1.2
- Another: [12, 21, 10, 18, 23, 15] → slope = +0.8

After 10,000 shuffles, we find that only 45 random arrangements produced a slope ≥ 2.6.

**P-value** = 45/10,000 = 0.0045 (0.45%)

**Conclusion**: There's less than a 0.5% chance that random fluctuation alone created this upward trend. The trend is **real and significant**!

## How does it work?

### Step 1: Measure the Observed Trend

**We calculate three key metrics from the actual data:**

1. **Slope (Trend)**: The rate of change over time
   - Positive slope = upward trend
   - Negative slope = downward trend
   - Example: +2.5 means "increases by 2.5 units per time period"

2. **Aggregated $R^2$**: How consistent is the trend at the group level?
   - We average values at each time point, then measure fit
   - Filters out individual noise to reveal the general direction
   - Closer to 1.0 = very consistent trend

3. **Raw $R^2$**: How much do individuals vary around the trend?
   - Usually lower because individuals are noisy
   - Shows how predictable individual behavior is

**Technical Implementation:**

+ **Trend:** First, we calculate slope on the raw data, which represents the observed magnitude and direction of the change.

+ **Aggregated $R^2$:** We calculate $R^2$ to provide a measure of the trend's reliability. By taking the mean value for each time point, we filter out individual level noise to reveal the general direction of the group.

+ **$R^2$:** We also retain the $R^2$ calculated on the raw data. While usually low, this metric indicates how much individual behaviour varies around the general trend.

#### SQL Implementation

<details>
<summary>Click to view SQL code</summary>

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
</details>

### Step 2: Create Random Universes (Simulations)

**The Goal**: Generate thousands of "fake" datasets where there's **no real trend**—just random noise.

**How?** We keep the time points fixed (Jan, Feb, Mar...) but randomly shuffle the values. This breaks any real time-value relationship while preserving the data's overall distribution.

**Creating Simulation Table**

+ To estimate the probability of observing such a trend by chance, we generate `n_iterations` of random datasets. We use `CROSS JOIN` with `EXPLODE` to replicate dataset.

<details>
<summary>Click to view SQL code</summary>

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
</details>

**The Shuffling Process: Breaking Time's Connection**

**The core logic**: Eliminate the relationship between time and value to simulate a "no trend" world.

**What we do**:
- **Time points stay fixed**: January is still January, February is still February
- **Values get randomized**: January's actual value might get randomly assigned to March
- This simulates a world where the values have no time-dependent pattern

**Think of it like this**:
> You have 12 numbered envelopes (months) and 12 values written on cards. In reality, the cards are in order inside the envelopes. We pull all cards out, shuffle them, and randomly put them back into the envelopes. If the original "in-order" arrangement produced a significantly stronger trend than the shuffled versions, the trend was real.

**Technical details**:
+ We keep the time column (`range_col`) ordered. Then, we randomize the `value_col` using `ROW_NUMBER() OVER (PARTITION BY iteration, {group_col} ORDER BY rand())` for each iteration.

+ Finally, we join the randomized values to the fixed time points using the condition: `ON a.iteration = b.iteration AND
       a.{group_col} = b.{group_col} AND
       a.rn = b.random_rn`.

+ Note that `b.{value_col}` represents the randomized values.

<details>
<summary>Click to view SQL code</summary>

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
</details>

### Step 3: Compare Real vs. Random

**Final Part - Simulation and P-Value Calculation:**

Now comes the moment of truth: **How unusual is our observed trend?**

+ For every simulated scenario (iteration), we calculate the slope of the shuffled data.

+ Finally, we determine the **P-Value** by calculating the proportion of random scenarios that produced a trend more extreme than our observed trend.

**Interpretation:**

+ **For Positive Trends (upward):** "Out of 10,000 random shuffles, how many produced a slope ≥ our observed slope?"
  - If only 200 did → p-value = 0.02 (2%)
  - Conclusion: Very unlikely by chance → **Significant upward trend!**

+ **For Negative Trends (downward):** "How many random shuffles produced a slope ≤ our observed slope?"
  - If only 50 did → p-value = 0.005 (0.5%)
  - Conclusion: Extremely unlikely by chance → **Significant downward trend!**

**The Bottom Line**: A low p-value (typically < 0.05) means that random chance rarely produces a trend as strong as what we observed. This confirms the trend is **statistically real**, not just noise.

<details>
<summary>Click to view SQL code</summary>

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
</details>
