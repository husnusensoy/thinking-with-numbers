import streamlit as st
import bq


@st.cache
def mean():
    return bq.run_sql("select avg(total_amount) mean from `analytics-bootcamp-323516.week1.trips_2015`")['mean'][0]


@st.cache
def weighted_mean():
    return bq.run_sql("""
    SELECT
  SUM(w*total_amount)/SUM(w) AS wmean
FROM (
  SELECT
    EXP(-DATE_DIFF(last_pickup_datetime, pickup_datetime, DAY)) w,
    DATE_DIFF(last_pickup_datetime, pickup_datetime, DAY) delta,
    total_amount
  FROM (
    SELECT
      pickup_datetime,
      MAX(pickup_datetime ) OVER() last_pickup_datetime,
      total_amount
    FROM
      `analytics-bootcamp-323516.week1.trips_2015` ) )
    """)['wmean'][0]


@st.cache
def truncated_mean(p):
    return bq.run_sql(f"""
    select avg(total_amount) tmean from 
(select total_amount, cume_dist() over(order by total_amount) p 
from `analytics-bootcamp-323516.week1.trips_2015` )
where p between {p} and {1 - p}
    """)['tmean'][0]


@st.cache
def median():
    return bq.run_sql(
        "select  percentile_cont(total_amount, 0.5) over() median from `analytics-bootcamp-323516.week1.trips_2015` limit 1")[
        'median'][0]


def render():
    st.title("Estimates of Location")

    st.header("Average/Mean")

    st.write(mean())

    st.markdown("""
    * Center of Mass
    * Not a robust estimate for central tendency
    """)

    st.header("Median/50th Percentile")
    st.write(median())

    st.header("Trimmed/Truncated Mean")
    tmean = truncated_mean(0.1)
    st.write(tmean)

    st.header("Weigted Mean/Average")

    wmean = weighted_mean()
    st.write(wmean)
