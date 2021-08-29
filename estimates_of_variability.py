import streamlit as st

import bq


@st.cache
def minmax():
    return bq.run_sql("""
    select max(total_amount) - min(total_amount) rng from `analytics-bootcamp-323516.week1.trips_2015`
    """)['rng'][0]


@st.cache
def mad():
    return bq.run_sql("""
    select avg(abs(total_amount - median)) mad from
(SELECT
  total_amount, percentile_cont(total_amount,
    0.5) OVER() median
FROM
  `analytics-bootcamp-323516.week1.trips_2015`)
    """)['mad'][0]


@st.cache
def var():
    return bq.run_sql("""
select VAR_POP(fare_amount) var_pop,  VAR_SAMP(fare_amount) var_sample
        from `analytics-bootcamp-323516.week1.trips_2015`;
    """)


@st.cache
def sd():
    return bq.run_sql("""
        select STDDEV_POP(fare_amount) sd_pop,  STDDEV_SAMP(fare_amount) sd_sample
        from `analytics-bootcamp-323516.week1.trips_2015`
    """)


@st.cache
def iqr():
    return bq.run_sql("""
    select q[offset(25)] q25, q[offset(75)]       q75 from
(select approx_quantiles(total_amount, 100) q from `analytics-bootcamp-323516.week1.trips_2015` )
    """).assign(iqr=lambda x: x.q75 - x.q25)

@st.cache
def iqr2():
    return bq.run_sql("""
   select q[offset(1)] q25, q[offset(3)]       q75 from
(select approx_quantiles(total_amount, 4) q from `analytics-bootcamp-323516.week1.trips_2015` )
    """).assign(iqr=lambda x: x.q75 - x.q25)


def render():
    st.title("Estimates of Variability")

    st.write(minmax())

    st.header("Mean Absolute Deviation (L1/Manhattan Norm)")

    st.write(mad())

    st.header("Variance (MSE)")

    st.write(var())

    st.header("Standard Deviation")

    st.write(sd())

    st.info("""
    `n` vs `n-1` (degrees of freedom) at denominator defines biased(population)/unbiased(sample) estimation.
    """)

    st.header("Inter Quartile Range (IQR)")
    df = iqr()

    st.dataframe(df)
    st.dataframe(iqr2())
