create or replace model  `analytics-bootcamp-323516.week1.fare_est`
OPTIONS(model_type = 'linear_reg', input_label_cols=['dep_y'],enable_global_explain=TRUE) as
select
  vendor_id,
  --  trip_distance,
  sqrt(POW(dropoff_latitude - pickup_latitude,2 ) + POW(dropoff_longitude - pickup_longitude,2 )) as estimated_distance_euc,
  abs(dropoff_latitude - pickup_latitude) + abs(dropoff_longitude - pickup_longitude) as estimated_distance_man,
  extract(hour
  from
    pickup_datetime) as hh24,
  payment_type,
  dropoff_longitude as lon,
  dropoff_latitude as lat,
  dropoff_longitude * dropoff_latitude as lonlat,
  passenger_count,
  fare_amount + tolls_amount as dep_y
from
  `analytics-bootcamp-323516.week1.trips_2015`
  TABLESAMPLE
SYSTEM(1
PERCENT)
LIMIT
  10000;

