import pandas as pd
import streamlit as st
from stqdm import stqdm

from helper import Comparator, perm_diff, stats_for_rand_events, visualize_hist

DEFAULT_N_TRIALS = 1000
MIN_TRIALS = 100
MAX_TRIALS = 2000
TRIAL_STEP = 50


def conversion_rate():
    st.title("Conversion Rate Example")
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

    n_price_b = (
        conv.loc[conv.outcome == "price_b", ["Conversion", "No conversion"]].sum(axis=1).values[0]
    )
    n_price_a = (
        conv.loc[conv.outcome == "price_a", ["Conversion", "No conversion"]].sum(axis=1).values[0]
    )

    perm_diffs = [
        perm_diff(balls, n_price_a, n_price_b)
        for _ in stqdm(range(n_trials), desc="Running Permutations")
    ]

    # st.write(perm_diffs)

    visualize_hist(perm_diffs, [obs_diff], "Distribution of Random Shuffle Differences")

    count, p_value, n_trials = stats_for_rand_events(
        perm_diffs, obs_diff, Comparator.SAMPLES_ARE_GREATER_THAN_OBS
    )

    st.write(
        f"Observed difference {obs_diff:.4f} (or more) is observed in {count:d} ({p_value:.4f}) trials out of {n_trials} trial."
    )
    st.write(
        f"We can not reject the null hypothesis at a significance level of 0.05. In other words, more than 5% of the trials ({p_value:.4f}) we observed a difference of {obs_diff:.4f} or greater by chance."
    )


def render():
    conversion_rate()


if __name__ == "__main__":
    render()
