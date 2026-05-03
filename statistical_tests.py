import streamlit as st

import anova
import conv_rate
import min_max
import t_test
import trend

DEFAULT_N_TRIALS = 1000
MIN_TRIALS = 100
MAX_TRIALS = 2000
TRIAL_STEP = 50


def render():

    pages = [
        st.Page(t_test.render, title="t-test", url_path="t-test"),
        st.Page(conv_rate.render, title="Conversion Rate", url_path="conversion-rate"),
        st.Page(anova.render, title="Are groups differ ? (ANOVA)", url_path="anova"),
        st.Page(min_max.render, title="Best/Worst (Min/Max Test)", url_path="min-max"),
        st.Page(trend.render, title="Water Consumption Trend (Trend Test)", url_path="trend"),
    ]

    pg = st.navigation(pages)

    pg.run()


if __name__ == "__main__":
    render()
