create or replace model `analytics-bootcamp-323516.week1.kmeans`
options(model_type='kmeans', num_clusters=2) as
select  fare_amount from `analytics-bootcamp-323516.week1.trips_2015`
TABLESAMPLE
SYSTEM(1
PERCENT)
LIMIT
  10000;
