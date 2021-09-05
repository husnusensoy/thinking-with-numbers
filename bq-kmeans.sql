create or replace model `analytics-bootcamp-323516.week1.geo_clusters`
options(model_type='kmeans', num_clusters=16) as
select   pickup_longitude lon, pickup_latitude  lat from `analytics-bootcamp-323516.week1.trips_2015`
TABLESAMPLE
SYSTEM(1
PERCENT)
LIMIT
  10000;
