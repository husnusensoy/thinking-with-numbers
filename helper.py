from enum import StrEnum
from math import fabs
from random import shuffle

import numpy as np
import pandas as pd
import plotly.express as px
import streamlit as st


class Comparator(StrEnum):
    TWO_SIDED = "two-sided"
    SAMPLES_ARE_GREATER_THAN_OBS = "samples are greater than observation"
    SAMPLES_ARE_SMALLER_THAN_OBS = "samples are smaller than observation"


def stats_for_rand_events(
    permutation_results: np.ndarray,
    observed_value: float,
    comparator: Comparator,
) -> tuple[int, float, int]:
    """Calculate p-value from permutation test results.

    Args:
        permutation_results: Array of permutation test statistics
        observed_value: The observed test statistic
        fn_compare: A function that takes two values and returns True if the first is more extreme than the second (e.g., operator.gt for greater, operator.lt for less)

    Returns:
        tuple: (count, p_value, n_trials)
    """
    perm_array = np.array(permutation_results)
    n_trials = len(perm_array)

    if comparator == Comparator.TWO_SIDED:
        count = np.sum(np.abs(perm_array) > fabs(observed_value))
    elif comparator == Comparator.SAMPLES_ARE_GREATER_THAN_OBS:
        count = np.sum(perm_array > observed_value)
    else:
        count = np.sum(perm_array < observed_value)

    p_value = count / n_trials

    return count, p_value, n_trials


def nullify_groups(df: pd.DataFrame) -> pd.DataFrame:
    """Randomly shuffle the values in the value column while keeping the group labels intact."""
    copy = df.copy()

    copy["Time"] = np.random.permutation(df["Time"].values)

    return copy


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
