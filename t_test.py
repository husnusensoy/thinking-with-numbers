from math import fabs

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st
from scipy import stats
from stqdm import stqdm

from helper import Comparator, perm_diff, stats_for_rand_events, visualize_hist

DEFAULT_N_TRIALS = 1000
MIN_TRIALS = 100
MAX_TRIALS = 2000
TRIAL_STEP = 50


def web_session_experiment():
    st.title("A Web Session Example")
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
        perm_diff(session.Time, n_b, n_a)
        for _ in stqdm(range(n_trials), desc="Running Permutations")
    ]

    count, p_value, n_trials = stats_for_rand_events(
        perm_diffs, true_diff, Comparator.SAMPLES_ARE_GREATER_THAN_OBS
    )

    st.write(
        f"Observed difference {true_diff:.4f} (or more) is observed in {count:d} ({p_value:.4f}) trials out of {n_trials} trial."
    )
    st.write(
        f"We can not reject the null hypothesis at a significance level of 0.05. In other words, more than 5% of the trials ({p_value:.2%}) we observed a difference of {true_diff:.4f} or greater by chance."
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

    count, p_value, n_trials = stats_for_rand_events(perm_diffs, true_diff, Comparator.TWO_SIDED)

    st.write(
        f"Observed difference {true_diff:.4f} (or more) is observed in {count:d} ({p_value:.4f}) trials out of {n_trials} trials."
    )

    perm_abs_diffs = [
        fabs(perm_diff(session.Time, n_a, n_b))
        for _ in stqdm(range(n_trials_2), desc="Running Permutations")
    ]

    visualize_hist(
        perm_abs_diffs, [true_diff], "Distribution of Random Shuffle Absolute Differences"
    )

    st.write(
        f"Observed difference {true_diff:.4f} (or more) is observed in {count:d} ({p_value:.4f}) trials out of {n_trials} trials."
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


def render():
    web_session_experiment()


if __name__ == "__main__":
    render()
