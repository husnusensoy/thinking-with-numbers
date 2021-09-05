import streamlit as st
from bq import run_sql

import seaborn as sns

st.set_option('deprecation.showPyplotGlobalUse', False)


@st.cache
def get_ts(vendor="CMT"):
    return run_sql(f"""
     select * from
(SELECT
  *
FROM
  ML.EXPLAIN_FORECAST(MODEL `analytics-bootcamp-323516.week1.revenue_arima` ,
                      STRUCT(360 AS horizon, 0.9 AS confidence_level)) 
order by time_series_timestamp desc 
limit 1000) order by time_series_type desc
    """)


def render():
    vendor = st.selectbox("Pick Vendor", ['CMT', 'VTS'])
    ts = get_ts(vendor)

    st.dataframe(ts)

    fig = sns.lineplot(x="time_series_timestamp", y="time_series_data", hue="vendor_id",
                       style="time_series_type", data=ts)

    st.write(fig)
    st.pyplot()
