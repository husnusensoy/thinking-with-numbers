import pandas as pd
import streamlit as st
from stqdm import stqdm

from helper import Comparator, nullify_groups, stats_for_rand_events, visualize_hist

DEFAULT_N_TRIALS = 1000
MIN_TRIALS = 100
MAX_TRIALS = 2000
TRIAL_STEP = 50


def perm_var(sess: pd.DataFrame) -> float:
    df = nullify_groups(sess)

    return df.groupby("Page").mean().var().values[0]


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

    _, p_value, _ = stats_for_rand_events(
        perm_vars, obs_var, Comparator.SAMPLES_ARE_GREATER_THAN_OBS
    )

    st.write(f"Pr(Prob) {p_value:.4f}... difference in variance {obs_var:.2f} ...")


def render():
    multiple_page_are_they_different()


if __name__ == "__main__":
    render()
