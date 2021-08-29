import bq
import streamlit as st
import seaborn as sns


@st.cache
def quantiles():
    return bq.run_sql("""
select q from 
(select approx_quantiles(total_amount, 100) quantiles 
    from `analytics-bootcamp-323516.week1.trips_2015` ), 
    unnest(quantiles) as q
    """)


@st.cache
def sample(n=1000):
    return bq.run_sql(f"""
 SELECT
    total_amount
  FROM
    `analytics-bootcamp-323516.week1.trips_2015` TABLESAMPLE SYSTEM (1 PERCENT) LIMIT {n}
    """)


@st.cache
def height_balanced():
    return bq.run_sql("""
    SELECT
  bin_number,
  MIN(total_amount) AS range_min,
  MAX(total_amount) AS range_max,
  COUNT(1) AS freq
FROM (
  SELECT
    NTILE(10) OVER (ORDER BY total_amount) bin_number,
    total_amount
  FROM
    `analytics-bootcamp-323516.week1.trips_2015`)
GROUP BY
  1
ORDER BY
  1
    """)


def render():
    st.title("Exploring Data Distribution")

    st.header("Percentiles and Boxplot")

    st.dataframe(quantiles().iloc[[5, 25, 50, 75, 95]])

    s = sample(10_000)

    st.write(sns.boxplot(data=s, x="total_amount"))
    st.pyplot()

    st.header("Frequency Tables & Histograms")
    st.subheader("Frequency Tables")

    st.dataframe(height_balanced())

    kde_enabled = st.checkbox("Kernel Density Estimator")
    st.write(sns.histplot(data=s, x="total_amount", kde=kde_enabled))

    st.pyplot()

    st.info("Gaussian mixture model fit")