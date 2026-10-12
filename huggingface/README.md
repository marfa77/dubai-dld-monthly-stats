---
license: cc-by-4.0
pretty_name: Dubai DLD Monthly Sales Statistics
language: [en]
size_categories: [10K<n<100K]
task_categories: [tabular-regression]
tags: [dubai, real-estate, dld, property-prices, open-data, time-series]
configs:
  - config_name: default
    data_files:
      - split: train
        path: dld_monthly_sales.csv
---

# Dubai DLD Monthly Sales Statistics

Monthly aggregates of Dubai Land Department registered property sales, 2026 year-to-date (Jan–Aug), 2026-01 to 2026-08: count, median price AED, median AED/sqft and off-plan share by area and property type. 112,220 transactions across 247 areas.

**Columns:** month, area, property_type, transactions, median_price_aed, median_aed_per_sqft, offplan_share, ready_share. `ALL` rows are totals.

**Source:** Dubai Land Department open data (attribution: Dubai Land Department / Dubai Government). Not an official DLD product. Aggregates only.

**Pipeline & updates:** https://github.com/marfa77/dubai-dld-monthly-stats

**Citation:** UAE Property (2026). dubai-dld-monthly-stats (v1.0.0) [Data set]. https://uaeproperty.vip
