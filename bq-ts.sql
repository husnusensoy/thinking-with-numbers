-- Time series mad using window functions...

-- HOLIDAY_REGION = 'GLOBAL'
CREATE or replace MODEL  `analytics-bootcamp-323516.week1.ts_arima`
OPTIONS(MODEL_TYPE='ARIMA_PLUS',
         time_series_timestamp_col='pickup_hh24',
         time_series_data_col='amount',
         time_series_id_col='vendor_id') AS
SELECT
  vendor_id,
  DATE_TRUNC(pickup_datetime, HOUR) pickup_hh24,
  SUM(total_amount - mta_tax-extra-imp_surcharge-tip_amount) AS amount
FROM
  `analytics-bootcamp-323516.week1.trips_2015`
GROUP BY
  1,
  2;

 SELECT
  vendor_id,
  DATE_TRUNC(pickup_datetime, DAY) pickup_day,
  SUM(total_amount - mta_tax-extra-imp_surcharge-tip_amount) AS amount
FROM
  `analytics-bootcamp-323516.week1.trips_2015`
GROUP BY
  1,
  2;


SELECT
  *
FROM
  ML.EXPLAIN_FORECAST(MODEL `analytics-bootcamp-323516.week1.ts_arima` ,
                      STRUCT(365 AS horizon, 0.9 AS confidence_level))
