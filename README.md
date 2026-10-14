# Dubai DLD monthly sales statistics (open dataset)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23322282.svg)](https://doi.org/10.5281/zenodo.23322282) [![PyPI](https://img.shields.io/pypi/v/dubai-dld-monthly-stats.svg)](https://pypi.org/project/dubai-dld-monthly-stats/)

[![npm](https://img.shields.io/npm/v/dubai-dld-monthly-stats.svg)](https://www.npmjs.com/package/dubai-dld-monthly-stats)

```sh
npm install dubai-dld-monthly-stats
```

Install: `pip install dubai-dld-monthly-stats`

Monthly aggregates of **registered property sales** in Dubai, built from the
[Dubai Land Department (DLD) open data](https://dubailand.gov.ae/en/open-data/real-estate-data/)
transactions feed. Covers **2026 year-to-date (Jan–Aug) (2026-01 – 2026-08), 8 complete months**, **247 areas**, **112,220 sales transactions**.

For each month × area × property type: transaction count, median price (AED), median AED/sqft,
and off-plan vs ready share.

- Data: [`data/dld_monthly_sales.csv`](data/dld_monthly_sales.csv) · [`data/dld_monthly_sales.json`](data/dld_monthly_sales.json)
- Interactive page with charts: https://marfa77.github.io/dubai-dld-monthly-stats/
- Pipeline: [`scripts/fetch_and_aggregate.py`](scripts/fetch_and_aggregate.py)

## Interactive demo

Try it on Hugging Face Spaces: [dubai-property-prices](https://huggingface.co/spaces/pablo2319/dubai-property-prices) — pick an area and month to see median sold price per m², sales count, MoM change and a chart.

## Columns

| column | meaning |
|---|---|
| month | YYYY-MM of DLD registration date (`INSTANCE_DATE`) |
| area | DLD area name (`AREA_EN`); `ALL` = Dubai-wide total |
| property_type | DLD property type (`Unit`, `Villa`, `Land`, `Building`); `ALL` = all types |
| transactions | number of sales transactions |
| median_price_aed | median transaction value, AED |
| median_aed_per_sqft | median of value ÷ (area m² × 10.7639) |
| offplan_share / ready_share | share of transactions flagged off-plan / ready |

## Methodology

1. `scripts/fetch_and_aggregate.py` queries the public DLD open-data endpoint
   (`gateway.dubailand.gov.ae/open-data/transactions`, group = Sales, no login) day by day.
2. Rows are de-duplicated by `TRANSACTION_NUMBER`; month = registration date.
3. All sales procedures in the DLD "Sales" group are included (incl. off-plan pre-registration).
   Zero-value rows count towards `transactions` but are excluded from medians; rows with no area are excluded from AED/sqft.
4. Medians (not means) are used to limit the effect of bulk/portfolio deals. Small cells (few transactions) are noisy — check `transactions` before comparing.

Reproduce: `python3 scripts/fetch_and_aggregate.py --start 2026-01 --end 2026-08 && python3 scripts/make_docs.py`

## Check a specific listing

Aggregates tell you the market; they don't tell you whether *one* broker offer is fair. To
[check a listing vs DLD sold prices](https://uaeproperty.vip) use UAE Property — first full DLD report free, then USD 1 per extra check or 5 checks for USD 5.

## Source & licence

- **Source:** Dubai Land Department, Open Data – Real Estate Transactions (accessed 2026-10-12). Also published via Dubai Pulse / Dubai Data (`dld_transactions-open`).
- DLD open data is published as Dubai Government open data under the Dubai Data Law (Law No. 26 of 2015) open-data terms, which allow use, copying, redistribution and derivative works, including commercially, with **attribution to the Dubai Government / Dubai Land Department**, without implying official endorsement, and without misleading use. This repository redistributes **aggregates only**, not raw records.
- This dataset is **not an official DLD product** and is not endorsed by DLD or the Dubai Government; no endorsement is implied.
- **Attribution:** Dubai Land Department / Dubai Government.
- Aggregated data: **CC BY 4.0** (`LICENSE-DATA`), with the DLD attribution above. Code: **MIT** (`LICENSE`).

## Citation

See [`CITATION.cff`](CITATION.cff). UAE Property (2026). *dubai-dld-monthly-stats* (v1.0.0) [Data set]. https://github.com/marfa77/dubai-dld-monthly-stats
