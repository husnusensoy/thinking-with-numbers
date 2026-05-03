import plotly.express as px
import streamlit as st

from dataset import make_time_series_data
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

    water = make_time_series_data()

    with st.expander("View Raw Data"):
        st.dataframe(water)

    st.subheader("Range Configuration")

    range_start, range_end = st.slider(
        "Select Month Range (MOY)", min_value=1, max_value=12, value=(1, 12), step=1
    )

    st.info(f"Analyzing trends from **Month {range_start}** to **Month {range_end}**.")

    filtered_water = water[(water["moy"] >= range_start) & (water["moy"] <= range_end)]

    st.subheader("Observed Trends")
    st.markdown("Visualizing the water consumption trend by month for each district.")

    fig = px.line(
        filtered_water.groupby(["moy", "district"])["m3"].mean().reset_index(),
        x="moy",
        y="m3",
        color="district",
        title="Water Consumption by Month and District",
    )
    fig.update_layout(xaxis_title="Month of Year", yaxis_title="Water Consumption (m³)")
    st.plotly_chart(fig, use_container_width=True)

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
        data=water,
        group_col="district",
        range_col="moy",
        value_col="m3",
        range_start=range_start,
        range_end=range_end,
        n_iterations=n_iterations,
    )

    obs_by_abs_trend = obs.sort_values("obs_trend", key=abs, ascending=False)

    st.dataframe(obs_by_abs_trend.style.format({"obs_trend": "{:.4f}"}))

    # st.dataframe(sim)

    district = st.selectbox(
        "Select District for Trend Analysis", options=obs_by_abs_trend["district"].unique()
    )

    visualize_hist(
        sim[sim.district == district]["obs_trend"],
        [obs[obs.district == district]["obs_trend"].values[0]],
        "Distribution of Trends with Randomized Trend",
    )


def render():
    trend_test()


if __name__ == "__main__":
    render()
