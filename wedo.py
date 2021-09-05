import streamlit as st

from bq import run_sql
import scipy.stats as stats
import seaborn as sns


def brand(brand):
    return run_sql(f"""
    select shipping,price from `analytics-bootcamp-323516.week2.mercari` where brand_name = "{brand}";
    """)


def candidates():
    return run_sql("""
WITH
  summa AS (
  SELECT
    *
  FROM (
    SELECT
      brand_name,
      shipping,
      AVG(price) ccost,
      COUNT(1) n
    FROM
      `analytics-bootcamp-323516.week2.mercari`
    GROUP BY
      1,
      2 )
  JOIN (
    SELECT
      brand_name,
      SUM(price) rev_by_brand,
      COUNT(1) n_by_brand
    FROM
      `analytics-bootcamp-323516.week2.mercari`
    GROUP BY
      1)
  USING
    (brand_name))
SELECT
  *
FROM
  summa a JOIN summa b on(a.shipping = 1 and b.shipping =0 and a.brand_name =b.brand_name and a.ccost between b.ccost-5 and b.ccost)
  order by a.n_by_brand desc;
    """)


def render():
    cands = candidates()

    for c in list(cands.brand_name):
        cost = brand(c)
        res = stats.ttest_ind(cost[cost.shipping == 0].price,
                              cost[cost.shipping == 1].price,
                              equal_var=False)
        st.write(f'p-value for single sided test: {res.pvalue / 2} for brand {c}')

        if res.pvalue / 2 <= 0.05:
            st.write(c)
            break

    st.dataframe(cost)

    fig = sns.histplot(data=cost, x="price", hue="shipping", kde=True)
    st.write(fig)
    st.pyplot()

    res = stats.ttest_ind(cost[cost.shipping == 0].price,
                          cost[cost.shipping == 1].price,
                          equal_var=False)
    st.write(f'p-value for single sided test: {res.pvalue / 2}')
