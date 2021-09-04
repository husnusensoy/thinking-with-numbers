import pandas as pd
import streamlit as st

import seaborn as sns
import numpy as np
import random

import scipy.stats as stats


def perm_diff(s, nA, nB):
    all_index = list(range(nA + nB))

    idx_A = set(random.sample(all_index, nA))

    idx_B = set(all_index) - idx_A

    mean_a = s.loc[idx_A].mean()

    mean_b = s.loc[idx_B].mean()

    return mean_b - mean_a


def conversion_rate():
    st.subheader("A Conversion Rate Example")
    conv = pd.DataFrame.from_dict(dict(outcome=['Conversion', 'No conversion'], price_a=[200, 23539],
                                       price_b=[182, 22406]))
    st.dataframe(conv)

    obs_diff = (200 / 23539 - 182 / 22406)
    st.write(f"Observed difference in conv rates is {obs_diff:.5f}")

    balls = [0] * (23539 + 22406)
    balls.extend([1] * (200 + 182))

    balls = pd.Series(balls)
    st.dataframe(balls)

    st.write(f"One experiment conv rate difference {perm_diff(balls, 23739, 182 + 22406)}")

    diffs = run_simulation(balls)

    st.write(
        f"Observed difference {obs_diff} (or more) probable in {np.mean(np.array(diffs) > obs_diff):.4f} trials out of 1000 trial")

    fig = sns.histplot(data=pd.DataFrame.from_dict(dict(diff=diffs)))
    fig.axvline(obs_diff, ls='--', c='r')
    st.write(fig, x="diff")
    st.pyplot()


@st.cache
def run_simulation(balls):
    perms_diff = []
    my_bar = st.progress(0)
    for i in range(1000):
        perms_diff.append(perm_diff(balls, 23739, 182 + 22406))

        my_bar.progress(i / 1000)

    return perms_diff


def render():
    st.header("To Statistical Testing by Simulation")
    c = st.sidebar.radio("Experiment Example", ["session", "price", "ANOVA"])

    if c == "session":
        web_session_experiment()
    elif c == "price":
        conversion_rate()
    else:
        anova()


def perm_var(sess):
    df = sess.copy()

    df['Time'] = np.random.permutation(df['Time'].values)
    return df.groupby('Page').mean().var()[0]


def anova():
    session = pd.DataFrame.from_dict(dict(
        Time=[164, 172, 177, 156, 195] + [178, 191, 182, 185, 177] + [175, 193, 171, 163, 176] + [155, 166, 164,
                                                                                                  170, 168],
        Page=['Page 1'] * 5 + ['Page 2'] * 5 + ['Page 3'] * 5 + ['Page 4'] * 5))

    st.dataframe(session)
    st.write(session.Time.mean())
    st.dataframe(session.groupby('Page').mean())
    st.dataframe(session.groupby('Page').var())

    obs_var = session.groupby('Page').mean().var()[0]

    n_sample = st.slider("Number of samples", 1000, 10_000, value=1000)
    perm_vars = [perm_var(session) for _ in range(n_sample)]
    #obs_var = session.groupby('Page').var().values
    fig = sns.histplot(data=pd.DataFrame.from_dict(dict(diff=perm_vars)))
    st.write(fig, x="diff")
    st.pyplot()

    st.write(f"Pr(Prob) {np.mean([var > obs_var for var in perm_vars]):.4f}... difference in variance {obs_var:.2f} ...")


def web_session_experiment():
    st.subheader("A Websesssion Example")
    st.text("""We have a data from an experiments showing average time spent in two pages by users.
    Trying to quantify whether Page B is really better than Page A ?
    """)
    session = pd.read_csv("data/web.csv")
    st.dataframe(session)
    st.markdown("## Summary Statistics")
    st.markdown("### Average time on Pages")
    st.dataframe(session.groupby("Page").mean())
    st.markdown("### Total hit on Pages")
    st.dataframe(session.groupby("Page").count())
    st.markdown("### BoxPlot for Time Distribution")
    st.write(sns.boxplot(data=session, x="Time", y="Page"))
    st.pyplot()
    nA, nB = 21, 15
    if st.checkbox("One Shot Experiment"):
        one_shot_experiment(nA, nB, session)
    st.markdown("## Let's Simulate")
    true_diff = session[session.Page == 'Page B'].mean() - session[session.Page == 'Page A'].mean()
    # st.write(true_diff)
    perm_diffs = [perm_diff(session.Time, nA, nB) for _ in range(1000)]
    st.write(
        f"Observed difference {true_diff[0]:.4f} (or more) probable in {np.mean(np.array(perm_diffs) > true_diff[0]):.4f} trials out of 1000 trial")
    fig = sns.histplot(data=pd.DataFrame.from_dict(dict(diff=perm_diffs)))
    fig.axvline(true_diff[0], ls='--', c='r')
    st.write(fig, x="diff")
    st.pyplot()

    res = stats.ttest_ind(session[session.Page == 'Page A'].Time,
                          session[session.Page == 'Page B'].Time,
                          equal_var=False)
    st.write(f'p-value for single sided test: {res.pvalue / 2:.4f}')


def one_shot_experiment(nA, nB, session):
    st.write("This function show details of a single trial")

    all_index = list(range(nA + nB))
    st.write(all_index)
    idx_A = set(random.sample(all_index, 21))
    st.write(idx_A)
    idx_B = set(all_index) - idx_A
    st.write(idx_B)
    st.subheader("Sample Set with idx A")
    mean_a = session.loc[idx_A].Time.mean()
    st.write(mean_a)
    st.subheader("Sample Set with idx B")
    mean_b = session.loc[idx_B]['Time'].mean()
    st.write(mean_b)
    st.subheader("Sample Set Mean time difference in 1 Experiment")
    st.write(mean_b - mean_a)
