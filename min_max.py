import numpy as np
import pandas as pd
import streamlit as st
from stqdm import stqdm

from helper import Comparator, nullify_groups, stats_for_rand_events, visualize_hist

DEFAULT_N_TRIALS = 1000
MIN_TRIALS = 100
MAX_TRIALS = 2000
TRIAL_STEP = 50


def compute_min_diff_for_the_best(d: dict, control_group: str) -> float:
    return min([d[control_group] - v for k, v in d.items() if k != control_group])


def compute_max_diff_for_the_worst(d: dict, control_group: str) -> float:
    return max([d[control_group] - v for k, v in d.items() if k != control_group])


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

    count, p_value, n_trials = stats_for_rand_events(
        fake_min_diffs, obs_min_diff, Comparator.SAMPLES_ARE_GREATER_THAN_OBS
    )

    st.write(
        f"Observed minimum difference {obs_min_diff:.4f} (or more) is observed in {count:d} ({p_value:.4f}) trials out of {n_trials} trial."
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

    count, p_value, n_trials = stats_for_rand_events(
        fake_max_diffs, obs_max_diff, Comparator.SAMPLES_ARE_SMALLER_THAN_OBS
    )

    st.write(
        f"Observed maximum difference {obs_max_diff:.4f} (or more) is observed in {count:d} ({p_value:.4f}) trials out of {n_trials} trial."
    )


def render():
    multiple_page_best_worst()


if __name__ == "__main__":
    render()
