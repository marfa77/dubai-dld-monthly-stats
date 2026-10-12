#!/usr/bin/env python3
"""Build README.md, docs/index.html (Dataset JSON-LD + charts), sitemap/robots and HF card from data/."""
import csv, datetime as dt, json, os, shutil
R = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
URL = "https://marfa77.github.io/dubai-dld-monthly-stats/"
rows = list(csv.DictReader(open(f"{R}/data/dld_monthly_sales.csv")))
months = sorted({r["month"] for r in rows})
areas = sorted({r["area"] for r in rows if r["area"] != "ALL"})
tot = {r["month"]: r for r in rows if r["area"] == "ALL" and r["property_type"] == "ALL"}
tx = sum(int(tot[m]["transactions"]) for m in months)
built = dt.date.today().isoformat()
v = dict(months=len(months), start=months[0], end=months[-1], areas=len(areas), tx=tx, built=built)
open(f"{R}/README.md", "w").write(open(f"{R}/README.template.md").read().format(**v))
last = months[-1]
top = sorted([r for r in rows if r["month"] == last and r["area"] != "ALL" and r["property_type"] == "ALL"], key=lambda r: -int(r["transactions"]))[:15]
desc = f"Monthly aggregates of Dubai Land Department registered property sales, 2026 year-to-date (Jan–Aug), {v["start"]} to {v["end"]}: count, median price AED, median AED/sqft and off-plan share by area and property type."
ld = {"@context": "https://schema.org", "@type": "Dataset", "name": "Dubai DLD monthly sales statistics", "description": desc,
      "url": URL, "sameAs": "https://github.com/marfa77/dubai-dld-monthly-stats", "license": "https://creativecommons.org/licenses/by/4.0/",
      "creator": {"@type": "Organization", "name": "UAE Property", "url": "https://uaeproperty.vip"},
      "isBasedOn": "https://dubailand.gov.ae/en/open-data/real-estate-data/", "temporalCoverage": f"{v['start']}/{v['end']}",
      "spatialCoverage": {"@type": "Place", "name": "Dubai, United Arab Emirates"}, "dateModified": built,
      "keywords": ["Dubai", "real estate", "DLD", "property prices", "open data"],
      "distribution": [{"@type": "DataDownload", "encodingFormat": "text/csv", "contentUrl": "https://raw.githubusercontent.com/marfa77/dubai-dld-monthly-stats/main/data/dld_monthly_sales.csv"},
                       {"@type": "DataDownload", "encodingFormat": "application/json", "contentUrl": "https://raw.githubusercontent.com/marfa77/dubai-dld-monthly-stats/main/data/dld_monthly_sales.json"}]}
series = {"labels": months, "n": [int(tot[m]["transactions"]) for m in months],
          "psf": [float(tot[m]["median_aed_per_sqft"] or 0) for m in months],
          "off": [round(100 * float(tot[m]["offplan_share"]), 1) for m in months]}
trs = "".join(f"<tr><td>{r['area']}</td><td>{int(r['transactions']):,}</td><td>{float(r['median_price_aed'] or 0):,.0f}</td><td>{float(r['median_aed_per_sqft'] or 0):,.0f}</td><td>{100*float(r['offplan_share']):.0f}%</td></tr>" for r in top)
html = f"""<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Dubai DLD monthly sales statistics (open data)</title><meta name="description" content="{desc}"><link rel="canonical" href="{URL}">
<script type="application/ld+json">{json.dumps(ld)}</script><script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
<style>body{{font-family:system-ui,sans-serif;max-width:960px;margin:2rem auto;padding:0 1rem;color:#222}}table{{border-collapse:collapse;width:100%}}td,th{{border-bottom:1px solid #ddd;padding:4px 8px;text-align:right}}td:first-child,th:first-child{{text-align:left}}canvas{{margin:1rem 0}}</style></head><body>
<h1>Dubai DLD monthly sales statistics</h1><p>{desc} {tx:,} transactions, {len(areas)} areas. Source: Dubai Land Department open data. Not an official DLD product.</p>
<p><a href="https://raw.githubusercontent.com/marfa77/dubai-dld-monthly-stats/main/data/dld_monthly_sales.csv">CSV</a> · <a href="https://raw.githubusercontent.com/marfa77/dubai-dld-monthly-stats/main/data/dld_monthly_sales.json">JSON</a> · <a href="https://github.com/marfa77/dubai-dld-monthly-stats">GitHub</a></p>
<h2>Sales per month (Dubai)</h2><canvas id="c1"></canvas><h2>Median AED/sqft and off-plan share</h2><canvas id="c2"></canvas>
<h2>Top areas by sales, {last}</h2><table><tr><th>Area</th><th>Sales</th><th>Median AED</th><th>Median AED/sqft</th><th>Off-plan</th></tr>{trs}</table>
<p>Have a specific broker offer? <a href="https://uaeproperty.vip">Check a listing vs DLD sold prices</a> — first full DLD report free, then USD 1 per extra check or 5 checks for USD 5.</p>
<p><small>Data: CC BY 4.0, attribution: Dubai Land Department / Dubai Government. Code: MIT. Built {built}.</small></p>
<script>const s={json.dumps(series)};
new Chart(c1,{{type:'bar',data:{{labels:s.labels,datasets:[{{label:'Sales transactions',data:s.n}}]}}}});
new Chart(c2,{{type:'line',data:{{labels:s.labels,datasets:[{{label:'Median AED/sqft',data:s.psf,yAxisID:'y'}},{{label:'Off-plan %',data:s.off,yAxisID:'y1'}}]}},options:{{scales:{{y1:{{position:'right'}}}}}}}});</script></body></html>"""
open(f"{R}/docs/index.html", "w").write(html)
open(f"{R}/docs/sitemap.xml", "w").write(f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"><url><loc>{URL}</loc><lastmod>{built}</lastmod></url></urlset>\n')
open(f"{R}/docs/robots.txt", "w").write(f"User-agent: *\nAllow: /\nSitemap: {URL}sitemap.xml\n")
open(f"{R}/docs/.nojekyll", "w").write("")
shutil.copy(f"{R}/data/dld_monthly_sales.csv", f"{R}/huggingface/dld_monthly_sales.csv")
open(f"{R}/huggingface/README.md", "w").write(f"""---
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

{desc} {tx:,} transactions across {len(areas)} areas.

**Columns:** month, area, property_type, transactions, median_price_aed, median_aed_per_sqft, offplan_share, ready_share. `ALL` rows are totals.

**Source:** Dubai Land Department open data (attribution: Dubai Land Department / Dubai Government). Not an official DLD product. Aggregates only.

**Pipeline & updates:** https://github.com/marfa77/dubai-dld-monthly-stats

**Citation:** UAE Property (2026). dubai-dld-monthly-stats (v1.0.0) [Data set]. https://uaeproperty.vip
""")
print(v)
