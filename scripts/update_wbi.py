#!/usr/bin/env python3
"""Holt den DWD-Waldbrandgefahrenindex (Station 13670) und schreibt data/wbi.json."""
import csv
import gzip
import json
import os
import urllib.request
from datetime import date, timedelta

STATION_ID = "13670"
SOURCE_URL = (
    "https://opendata.dwd.de/climate_environment/CDC/derived_germany/"
    "fire_danger_index/woodland/forecast/recent/"
    f"derived_germany_fire_danger_index_woodland_forecast_recent_{STATION_ID}_v2-3--0.csv.gz"
)
OUTPUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "wbi.json")


def fetch_latest_row():
    req = urllib.request.Request(SOURCE_URL, headers={"User-Agent": "wbi-widget/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = gzip.decompress(resp.read())
    text = raw.decode("utf-8")
    rows = list(csv.reader(text.strip().splitlines(), delimiter=";"))
    header, data_rows = rows[0], rows[1:]
    if not data_rows:
        raise RuntimeError("Keine Datenzeilen in der DWD-CSV gefunden")
    return data_rows[-1]  # jüngste Vorhersage steht am Dateiende


def build_payload(row):
    termin = row[1]  # Format "YYYYMMDD HH:MM"
    base_date = date(int(termin[0:4]), int(termin[4:6]), int(termin[6:8]))
    days = []
    for i in range(7):  # wbi_0 (heute) .. wbi_6 (heute + 6 Tage)
        days.append({
            "date": (base_date + timedelta(days=i)).isoformat(),
            "stufe": int(row[2 + i]),
        })
    return {
        "station": STATION_ID,
        "updated": termin,
        "days": days,
    }


def main():
    row = fetch_latest_row()
    payload = build_payload(row)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print(f"geschrieben: {OUTPUT_PATH} -> {payload}")


if __name__ == "__main__":
    main()
