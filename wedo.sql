-- Try to detect disadvantage for customers paying shipping per brand.
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

