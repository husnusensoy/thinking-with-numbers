from pyspark.sql import SparkSession

def trend_perm(
    data_path: str,
    group_col: str,
    range_col: str,
    value_col: str,
    range_start: int,
    range_end: int,
    n_iterations: int = 2,
):
    spark = SparkSession.builder \
    .config("spark.driver.memory", "6g") \
    .getOrCreate()

    spark.read.csv(
        data_path,
        header=True,
        inferSchema=True,
    ).createOrReplaceTempView("_data")

    return spark.sql(
        f"""
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
        o.{group_col},
        o.obs_trend,
        o.r_squared,
        AVG(
            CASE 
                WHEN o.obs_trend > 0 AND p.perm_trend >= o.obs_trend THEN 1
                WHEN o.obs_trend < 0 AND p.perm_trend <= o.obs_trend THEN 1
                ELSE 0
            END
        ) AS p_value,
        {n_iterations} AS n_iterations
    FROM 
        perm_trends p
    JOIN 
        observed_trend o ON p.{group_col} = o.{group_col}
    GROUP BY 
        1,2,3

    """
    ).toPandas()