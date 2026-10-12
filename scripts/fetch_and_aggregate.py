#!/usr/bin/env python3
"""Fetch Dubai Land Department (DLD) open-data sales transactions and build
monthly aggregates by area and property type.

Source: DLD Open Data, https://dubailand.gov.ae/en/open-data/real-estate-data/
(public endpoint https://gateway.dubailand.gov.ae/open-data/transactions, no login).
Usage: python scripts/fetch_and_aggregate.py --start 2026-01 --end 2026-08
Only aggregates are written; raw rows are cached locally in .cache/ (git-ignored).
"""
import argparse, csv, datetime as dt, gzip, json, os, statistics, time, urllib.request
from collections import defaultdict

API = "https://gateway.dubailand.gov.ae/open-data/transactions"
SQM_TO_SQFT = 10.7639
CACHE = ".cache"

def post(body, tries=6):
    data = json.dumps(body).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(API, data=data, headers={"Content-Type": "application/json", "User-Agent": "dubai-dld-monthly-stats/1.0"})
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)["response"]["result"]
        except Exception as e:
            time.sleep(5 * (i + 1)); err = e
    raise err

def fetch_day(d):
    os.makedirs(CACHE, exist_ok=True)
    fn = os.path.join(CACHE, f"{d.isoformat()}.json.gz")
    if os.path.exists(fn):
        return json.load(gzip.open(fn, "rt"))
    nxt = d + dt.timedelta(days=1)
    rows, skip = [], 0
    while True:
        res = post({"P_FROM_DATE": d.strftime("%m/%d/%Y"), "P_TO_DATE": nxt.strftime("%m/%d/%Y"),
                    "P_GROUP_ID": "1", "P_IS_OFFPLAN": "", "P_IS_FREE_HOLD": "", "P_AREA_ID": "",
                    "P_USAGE_ID": "", "P_PROP_TYPE_ID": "", "P_TAKE": "5000", "P_SKIP": str(skip),
                    "P_SORT": "TRANSACTION_NUMBER_ASC"})
        rows += res
        if not res or len(rows) >= res[0]["TOTAL"]:
            break
        skip += len(res)
    keep = ("TRANSACTION_NUMBER", "INSTANCE_DATE", "PROCEDURE_EN", "IS_OFFPLAN", "AREA_EN",
            "PROP_TYPE_EN", "PROP_SB_TYPE_EN", "USAGE_EN", "TRANS_VALUE", "ACTUAL_AREA", "PROCEDURE_AREA")
    rows = [{k: r.get(k) for k in keep} for r in rows]
    json.dump(rows, gzip.open(fn, "wt"))
    return rows

def med(x): return round(statistics.median(x), 2) if x else None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--start", required=True); ap.add_argument("--end", required=True)
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    y, m = map(int, a.start.split("-")); ey, em = map(int, a.end.split("-"))
    d = dt.date(y, m, 1)
    end = (dt.date(ey + em // 12, em % 12 + 1, 1))
    seen, groups = set(), defaultdict(lambda: {"n": 0, "p": [], "psf": [], "off": 0})
    while d < end:
        for r in fetch_day(d):
            tn = r["TRANSACTION_NUMBER"]
            if tn in seen or not r["INSTANCE_DATE"]: continue
            seen.add(tn)
            mon = r["INSTANCE_DATE"][:7]
            if not (a.start <= mon <= a.end): continue
            v = r["TRANS_VALUE"] or 0
            area_sqm = r["ACTUAL_AREA"] or r["PROCEDURE_AREA"] or 0
            for key in [(mon, r["AREA_EN"] or "UNKNOWN", r["PROP_TYPE_EN"] or "UNKNOWN"), (mon, "ALL", r["PROP_TYPE_EN"] or "UNKNOWN"), (mon, "ALL", "ALL")]:
                g = groups[key]; g["n"] += 1; g["off"] += 1 if r["IS_OFFPLAN"] == 1 else 0
                if v > 0: g["p"].append(v)
                if v > 0 and area_sqm > 0: g["psf"].append(v / (area_sqm * SQM_TO_SQFT))
        d += dt.timedelta(days=1)
    os.makedirs(a.out, exist_ok=True)
    cols = ["month", "area", "property_type", "transactions", "median_price_aed", "median_aed_per_sqft", "offplan_share", "ready_share"]
    out = []
    for (mon, area, pt), g in sorted(groups.items()):
        off = round(g["off"] / g["n"], 4)
        out.append(dict(zip(cols, [mon, area, pt, g["n"], med(g["p"]), med(g["psf"]), off, round(1 - off, 4)])))
    with open(os.path.join(a.out, "dld_monthly_sales.csv"), "w", newline="") as f:
        w = csv.DictWriter(f, cols); w.writeheader(); w.writerows(out)
    json.dump(out, open(os.path.join(a.out, "dld_monthly_sales.json"), "w"), indent=1)
    print(f"{len(seen)} transactions, {len(out)} rows")

if __name__ == "__main__":
    main()
