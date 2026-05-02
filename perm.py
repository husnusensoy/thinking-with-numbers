from math import fabs
from random import shuffle

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats
from stqdm import stqdm

from trend_perm import trend_perm

DEFAULT_N_TRIALS = 1000
MIN_TRIALS = 100
MAX_TRIALS = 2000
TRIAL_STEP = 50


def compute_min_diff_for_the_best(d: dict, control_group: str) -> float:
    return min([d[control_group] - v for k, v in d.items() if k != control_group])


def compute_max_diff_for_the_worst(d: dict, control_group: str) -> float:
    return max([d[control_group] - v for k, v in d.items() if k != control_group])


def perm_diff(s: pd.Series, n_a: int, n_b: int, verbose: bool = False) -> float:
    """Take a dataset and randomly split it into two groups of size n_a and n_b,
    then return the difference in means between the two groups."""

    all_index = list(range(n_a + n_b))

    shuffle(all_index)

    idx_a = all_index[:n_a]

    idx_b = all_index[n_a : n_a + n_b]

    mean_a = s.loc[idx_a].mean()

    mean_b = s.loc[idx_b].mean()

    if verbose:
        st.write("Sample A Indices:", idx_a)
        st.write("Sample B Indices:", idx_b)
        st.write("Mean Time for Sample A:", mean_a)
        st.write("Mean Time for Sample B:", mean_b)
        st.write("Mean Time Difference Between Samples:", mean_b - mean_a)

    return mean_b - mean_a


def conversion_rate():
    st.subheader("A Conversion Rate Example")
    conv = pd.DataFrame.from_dict(
        {
            "outcome": ["price_a", "price_b"],
            "Conversion": [200, 182],
            "No conversion": [23539, 22406],
        }
    ).assign(conversion_rate=lambda df: df["Conversion"] / (df["Conversion"] + df["No conversion"]))
    st.dataframe(conv)

    obs_diff = (
        conv.loc[conv.outcome == "price_a", "conversion_rate"].values[0]
        - conv.loc[conv.outcome == "price_b", "conversion_rate"].values[0]
    )
    st.write(f"Observed difference in conv rates is {obs_diff:.5f}")

    converged_count = conv["Conversion"].sum()
    non_converged_count = conv["No conversion"].sum()

    balls = [0] * non_converged_count
    balls.extend([1] * converged_count)

    balls = pd.Series(balls)

    #    diffs = run_simulation(balls)

    n_trials = st.slider(
        "Number of Trials for Convergence",
        min_value=MIN_TRIALS,
        max_value=MAX_TRIALS,
        value=DEFAULT_N_TRIALS,
        step=TRIAL_STEP,
    )

    perm_diffs = [
        perm_diff(
            balls,
            conv.loc[conv.outcome == "price_b", ["Conversion", "No conversion"]]
            .sum(axis=1)
            .values[0],
            conv.loc[conv.outcome == "price_a", ["Conversion", "No conversion"]]
            .sum(axis=1)
            .values[0],
        )
        for _ in stqdm(range(n_trials), desc="Running Permutations")
    ]

    # st.write(perm_diffs)

    visualize_hist(perm_diffs, [obs_diff], "Distribution of Random Shuffle Differences")

    st.write(
        f"Observed difference {obs_diff:.4f} (or more) is observed in {np.sum(np.array(perm_diffs) > obs_diff):d} ({np.mean(np.array(perm_diffs) > obs_diff):.4f}) trials out of {n_trials} trial."
    )
    st.write(
        f"We can not reject the null hypothesis at a significance level of 0.05. In other words, more than 5% of the trials ({np.mean(np.array(perm_diffs) > obs_diff):.2%}) we observed a difference of {obs_diff:.4f} or greater by chance."
    )


def render():
    st.header("To Statistical Testing by Simulation")
    (
        session_tab,
        conversion_rate_tab,
        multiple_page_anova_tab,
        multiple_page_best_worst_tab,
        water_tab,
    ) = st.tabs(
        [
            "Session (t-test)",
            "Conversion Rate (t-test)",
            "Multiple Page (ANOVA)",
            "Multiple Page Best/Worst",
            "Water Consumption",
        ]
    )

    with session_tab:
        web_session_experiment()

    with conversion_rate_tab:
        conversion_rate()

    with multiple_page_anova_tab:
        multiple_page_are_they_different()

    with multiple_page_best_worst_tab:
        multiple_page_best_worst()

    with water_tab:
        water_consumption_experiment()


def nullify_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Randomly shuffle the values in the value column while keeping the group labels intact."""
    copy = df.copy()

    copy["Time"] = np.random.permutation(df["Time"].values)

    return copy


def perm_var(sess: pd.DataFrame) -> float:
    df = nullify_groups(sess)

    return df.groupby("Page").mean().var().values[0]


def multiple_page_best_worst():
    raw_data = {
        "Page 1": [164, 172, 177, 156, 195],
        "Page 2": [178, 191, 182, 185, 177],
        "Page 3": [175, 193, 171, 163, 176],
        "Page 4": [155, 166, 164, 170, 168],
    }

    session = pd.DataFrame(raw_data).melt(var_name="Page", value_name="Time")

    st.markdown("### Raw Session Data")

    st.dataframe(session)

    st.write(
        "Now let's try to quantify whether Page 2 has the highest time and Page 4 has the lowest time"
    )

    obs_means = session.groupby("Page")["Time"].mean().to_dict()

    st.write(obs_means)

    st.markdown("### Is Page 2 the best one ?")

    control_group = "Page 2"
    obs_min_diff = compute_min_diff_for_the_best(obs_means, control_group=control_group)

    if obs_min_diff < 0:
        st.error(f"{control_group} is not the best one")

    if obs_min_diff > 0:
        st.info(f"{control_group} is the best one")

    n_iterations = st.slider(
        "Number of Permutations",
        min_value=MIN_TRIALS,
        max_value=MAX_TRIALS,
        value=DEFAULT_N_TRIALS,
        step=TRIAL_STEP,
    )

    fake_min_diffs = np.zeros(n_iterations)

    for i in stqdm(range(n_iterations), desc="Running Permutations"):
        fake = nullify_groups(session)
        fake_means = fake.groupby("Page")["Time"].mean().to_dict()

        fake_min_diffs[i] = compute_min_diff_for_the_best(fake_means, control_group="Page 2")

    visualize_hist(fake_min_diffs, [obs_min_diff], "Distribution of Minimum Differences")

    st.write(
        f"Observed minimum difference {obs_min_diff:.4f} (or more) is observed in {np.sum(fake_min_diffs > obs_min_diff):d} ({np.mean(fake_min_diffs > obs_min_diff):.4f}) trials out of {n_iterations} trial."
    )

    st.markdown("### What about the worst one ?")
    control_group = "Page 4"
    obs_max_diff = compute_max_diff_for_the_worst(obs_means, control_group=control_group)

    if obs_max_diff < 0:
        st.info(f"{control_group} is the worst one with {obs_max_diff:.4f} max difference")

    if obs_max_diff > 0:
        st.error(f"{control_group} is not the worst one with {obs_max_diff:.4f} max difference")

    fake_max_diffs = np.zeros(n_iterations)

    for i in stqdm(range(n_iterations), desc="Running Permutations"):
        fake = nullify_groups(session)
        fake_means = fake.groupby("Page")["Time"].mean().to_dict()

        fake_max_diffs[i] = compute_max_diff_for_the_worst(fake_means, control_group="Page 4")

    visualize_hist(fake_max_diffs, [obs_max_diff], "Distribution of Maximum Differences")

    st.write(
        f"Observed maximum difference {obs_max_diff:.4f} (or more) is observed in {np.sum(fake_max_diffs < obs_max_diff):d} ({np.mean(fake_max_diffs < obs_max_diff):.4f}) trials out of {n_iterations} trial."
    )


def multiple_page_are_they_different():
    st.subheader("Multiple Page Experiment")
    raw_data = {
        "Page 1": [164, 172, 177, 156, 195],
        "Page 2": [178, 191, 182, 185, 177],
        "Page 3": [175, 193, 171, 163, 176],
        "Page 4": [155, 166, 164, 170, 168],
    }

    session = pd.DataFrame(raw_data).melt(var_name="Page", value_name="Time")

    st.markdown("### Raw Session Data")

    st.dataframe(session)
    st.write(f"Observed mean: {session.Time.mean():.4f}")

    st.markdown("### Summary Statistics")
    st.dataframe(session.groupby("Page").mean())
    st.dataframe(session.groupby("Page").var())

    obs_var = session.groupby("Page").mean().var().values[0]

    st.write(f"Observed variance of means: {obs_var:.4f}")

    n_sample = st.slider("Number of samples", 100, 10_000, value=100)

    perm_vars = [perm_var(session) for _ in stqdm(range(n_sample), desc="Running trials")]

    visualize_hist(perm_vars, [obs_var], "Distribution of Variance of Means from Permutations")

    st.write(
        f"Pr(Prob) {np.mean([var > obs_var for var in perm_vars]):.4f}... difference in variance {obs_var:.2f} ..."
    )


def visualize_hist(data, vlines, title):
    fig = px.histogram(data_frame=pd.DataFrame({"diff": data}), x="diff", nbins=50, title=title)
    for vline in vlines:
        fig.add_vline(
            x=vline,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Observed Diff: {vline:.4f}",
        )
    st.plotly_chart(fig)


def web_session_experiment():
    st.subheader("A Web Session Example")
    st.markdown("""
    We have data from an experiment showing average time spent on two pages by users.
    Trying to quantify whether **Page B** is really better than **Page A** in terms of user engagement ?
    """)
    session = pd.read_csv("data/web.csv")
    st.dataframe(session)

    st.markdown("## Summary Statistics")
    st.markdown("### Average time on Pages")

    agg_session = session.groupby("Page").agg(["mean", "var", "count"])

    st.dataframe(agg_session["Time"]["mean"])

    st.markdown("### Total hit on Pages")
    st.dataframe(agg_session["Time"]["count"])

    st.markdown("### Box plots for Time Distribution")

    fig = px.box(data_frame=session, x="Page", y="Time", points="all")
    st.plotly_chart(fig)

    st.markdown("## Try to Solve with Permutation Test")

    n_a, n_b = agg_session["Time"]["count"]["Page A"], agg_session["Time"]["count"]["Page B"]

    st.markdown("### Is Page B better than Page A ?")
    st.markdown(f"""
        - $H_0$: Page B is not better than Page A. Any random split of size {n_a} and {n_b} would show a difference or above by chance.
    """)

    st.markdown(f"""Experiment design:
- We will randomly shuffle the Time values and split them into two groups of size {n_a} and {n_b}.

- We will calculate the difference in mean Time between the two groups (Page B - Page A).

- We will collect frequencies of observing each difference.

- Finally we calculate the frequency of observing a value above the true difference in mean Time between Page B and Page A.

- If this frequency is very low, we can reject the null hypothesis and conclude that Page B is likely better than Page A in terms of user engagement.
    """)

    if st.checkbox("Let's see how one experiment looks like", value=False):
        perm_diff(session.Time, n_a, n_b, verbose=True)

    true_diff = (
        session[session.Page == "Page B"].Time.mean()
        - session[session.Page == "Page A"].Time.mean()
    )

    n_trials = st.slider("Number of Trials", min_value=100, max_value=2000, value=1000, step=50)

    perm_diffs = [
        perm_diff(session.Time, n_a, n_b)
        for _ in stqdm(range(n_trials), desc="Running Permutations")
    ]
    st.write(
        f"Observed difference {true_diff:.4f} (or more) is observed in {np.sum(np.array(perm_diffs) > true_diff):d} ({np.mean(np.array(perm_diffs) > true_diff):.4f}) trials out of {n_trials} trial."
    )
    st.write(
        f"We can not reject the null hypothesis at a significance level of 0.05. In other words, more than 5% of the trials ({np.mean(np.array(perm_diffs) > true_diff):.2%}) we observed a difference of {true_diff:.4f} or greater by chance."
    )

    visualize_hist(perm_diffs, [true_diff], "Distribution of Random Shuffle Differences")

    st.write("Let's verify simulation results with a standard t-test")

    res = stats.ttest_ind(
        session[session.Page == "Page A"].Time,
        session[session.Page == "Page B"].Time,
        equal_var=False,
    )
    st.write(f"p-value for single sided test: {res.pvalue / 2:.4f}")

    st.markdown("### Is there a real difference ?")

    st.markdown(f"""Experiment design:
- Randomly shuffle the Time values and split them into two groups of size {n_a} and {n_b}.

- Calculate the absolute difference in mean Time between the two groups (Page B - Page A).

- Collect frequencies of observing each difference.

- Calculate the frequency of observing a difference equal to or greater than the true observed difference.
    """)

    n_trials_2 = st.slider("Number of Trials 2", min_value=100, max_value=2000, value=1000, step=50)

    perm_abs_diffs = [
        fabs(perm_diff(session.Time, n_a, n_b))
        for _ in stqdm(range(n_trials_2), desc="Running Permutations")
    ]

    st.write(
        f"Observed difference {true_diff:.4f} (or more) is observed in {np.sum(np.array(perm_abs_diffs) > fabs(true_diff)):.0f} ({np.mean(np.array(perm_abs_diffs) > fabs(true_diff)):.4f}) trials out of {n_trials_2} trials."
    )

    visualize_hist(
        perm_abs_diffs, [true_diff], "Distribution of Random Shuffle Absolute Differences"
    )

    st.write(
        f"Observed difference {true_diff:.4f} (or more) is observed in {np.sum((np.array(perm_diffs) > fabs(true_diff)) | (np.array(perm_diffs) < -fabs(true_diff))):.0f} ({np.mean((np.array(perm_diffs) > fabs(true_diff)) | (np.array(perm_diffs) < -fabs(true_diff))):.4f}) trials out of {n_trials_2} trials."
    )

    visualize_hist(
        perm_diffs, [-true_diff, true_diff], "Distribution of Random Shuffle Differences"
    )

    st.write(
        f"We can not reject the null hypothesis at a significance level of 0.05. In other words, more than 5% of the trials ({np.mean(np.array(perm_diffs) > fabs(true_diff)):.2%}) we observed a difference of {true_diff:.4f} or greater by chance."
    )

    st.markdown(f"""
        - $H_0$: Absolute difference of {abs(true_diff):.4f} is not significant. Any random split of size {n_a} and {n_b} would show an absolute difference of this magnitude or greater by chance.
    """)

    two_sided_p_value = np.mean(np.abs(np.array(perm_diffs)) >= np.abs(true_diff))
    st.write(
        f"**Two-sided Test:** An absolute difference of {true_diff:.4f} (or greater) would occur in "
        f"**{two_sided_p_value:.1%}** of random permutations ({int(two_sided_p_value * n_trials)} out of {n_trials} trials). "
        f"This corresponds to a p-value of **{two_sided_p_value:.4f}**."
    )

    st.write(f"Calculated p-value for double sided test: {res.pvalue:.4f}")


def water_consumption_experiment():
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


if __name__ == "__main__":
    render()
