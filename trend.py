import pandas as pd
import streamlit as st

from helper import visualize_hist
from trend_perm import trend_perm

DEFAULT_N_TRIALS = 1000
MIN_TRIALS = 100
MAX_TRIALS = 2000
TRIAL_STEP = 50


def trend_test():
    st.header("Water Consumption Trend Analysis")
    st.markdown("""
    This experiment analyzes monthly water consumption data from smart meter readings to detect significant trends in different districts.
    """)

    water = pd.read_csv("data/water_consumption.csv", index_col=0)

    with st.expander("View Raw Data"):
        st.dataframe(water)

    st.subheader("Range Configuration")

    range_start, range_end = st.slider(
        "Select Month Range (MOY)", min_value=1, max_value=12, value=(1, 12), step=1
    )

    st.info(f"Analyzing trends from **Month {range_start}** to **Month {range_end}**.")

    filtered_water = water[(water["moy"] >= range_start) & (water["moy"] <= range_end)]

    st.subheader("Observed Trends")
    st.markdown(
        "Visualizing the average water consumption trend over the months for each district."
    )
    st.line_chart(filtered_water.groupby(["moy", "district"])["m3"].mean().unstack())

    st.subheader("Permutation Test")
    st.markdown("""
    We will now run the **Trend Permutation Test**.
    * **Slope:** The magnitude and direction of the trend (+/-).
    * **Mean R²:** How consistent the trend is.
    * **P-Value:** Probability that this trend occurred by chance.
    """)

    n_iterations = st.slider(
        "Number of Trials (Trend Test)",
        min_value=MIN_TRIALS,
        max_value=MAX_TRIALS,
        value=DEFAULT_N_TRIALS,
        step=TRIAL_STEP,
    )

    obs, sim = trend_perm(
        data_path="data/water_consumption.csv",
        group_col="district",
        range_col="moy",
        value_col="m3",
        range_start=range_start,
        range_end=range_end,
        n_iterations=n_iterations,
    )

    st.dataframe(
        obs.sort_values("obs_trend", ascending=False).style.format({"obs_trend": "{:.4f}"})
    )

    # st.dataframe(sim)

    district = st.selectbox("Select District for Trend Analysis", options=obs["district"].unique())

    visualize_hist(
        sim[sim.district == district]["obs_trend"],
        [obs[obs.district == district]["obs_trend"].values[0]],
        "Distribution of Trends with Randomized Trend",
    )


def render():
    trend_test()


if __name__ == "__main__":
    render()
