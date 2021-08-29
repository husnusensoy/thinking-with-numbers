import pandas as pd
import streamlit as st
import numpy as np
import seaborn as sns


def render():
    n = st.slider("Number of samples", 100, 100_000, value=1_000, step=100)
    distribution = st.selectbox("Distribution", ["expo", "unif", "pois", "norm", "bern", "bino"])

    if distribution == "expo":
        d = dict(sample=np.random.exponential(1, n))
    elif distribution == "unif":
        d = dict(sample=np.random.uniform(0, 10, n))
    elif distribution == "pois":
        d = dict(sample=np.random.poisson(3, n))
    elif distribution == "norm":
        d = dict(sample=np.random.normal(0, 1, n))
    elif distribution == "bern":
        d = dict(sample=np.random.binomial(1, p=0.8, size=n))
    elif distribution == "bino":
        d = dict(sample=np.random.binomial(97, p=0.4, size=n))

    df = pd.DataFrame.from_dict(d)

    st.dataframe(df.head())

    fig = sns.displot(data=df, x="sample", kde=True)

    st.pyplot(fig)

    m = st.slider("Game Count", 10, 10_000, step=10)
    n_observe = st.selectbox("Number Observed", [3, 10, 100, 1000, 10_000])
    mu = []
    for _ in range(m):

        if distribution == "expo":
            d = dict(sample=np.random.exponential(1, n_observe))
        elif distribution == "unif":
            d = dict(sample=np.random.uniform(0, 10, n_observe))
        elif distribution == "pois":
            d = dict(sample=np.random.poisson(3, n_observe))
        elif distribution == "norm":
            d = dict(sample=np.random.normal(0, 1, n_observe))
        elif distribution == "bern":
            d = dict(sample=np.random.binomial(1, p=0.8, size=n_observe))
        elif distribution == "bino":
            d = dict(sample=np.random.binomial(97, p=0.4, size=n_observe))

        d = pd.DataFrame.from_dict(d)

        mu.append(d['sample'].mean())
        # sigma = d['sample'].vars()

    mus = pd.DataFrame.from_dict(dict(sample=mu))

    fig = sns.displot(data=mus, x="sample", kde=False)

    st.write(mus.mean())
    st.write(mus.var())

    st.pyplot(fig)
