import duckdb
import pandas as pd
from tqdm import trange


def calculate_trend(
    df: pd.DataFrame, group_col: str, range_col: str, value_col: str
) -> pd.DataFrame:
    duckdb.register("df", df)

    return (
        duckdb.sql(f"""
    SELECT
        {group_col},
        REGR_SLOPE({value_col}, {range_col}) AS obs_trend,
        REGR_R2({value_col}, {range_col}) AS r_squared
    FROM
        df
    GROUP BY
        {group_col}
    """)
        .to_df()
        .to_dict("records")
    )


def trend_perm(
    data_path: str,
    group_col: str,
    range_col: str,
    value_col: str,
    range_start: int,
    range_end: int,
    n_iterations: int = 2,
):
    raw = pd.read_csv(data_path)

    duckdb.register("raw", raw)

    filtered_data = duckdb.sql(f"""
                               SELECT
            {group_col},
            {range_col},
            {value_col}
        FROM
            raw
        WHERE
            {range_col} BETWEEN {range_start} AND {range_end}
        ORDER BY
            {range_col}
        """).to_df()

    # print(filtered_data.head())

    observed_trend = calculate_trend(filtered_data, group_col, range_col, value_col)

    print(observed_trend)

    fake_trends = []
    for _ in trange(n_iterations, desc="Running Permutations"):
        copy = filtered_data.copy()

        for group in copy[group_col].unique():
            mask = copy[group_col] == group
            copy.loc[mask, value_col] = copy.loc[mask, value_col].sample(frac=1).values

        fake_trends += calculate_trend(copy, group_col, range_col, value_col)
        # Store fake_slope for p-value calculation

    return pd.DataFrame(observed_trend), pd.DataFrame(fake_trends)


if __name__ == "__main__":
    result = trend_perm(
        data_path="data/water_consumption.csv",
        group_col="district",
        range_col="moy",
        value_col="m3",
        range_start=1,
        range_end=12,
        n_iterations=1000,
    )
    print(result)
