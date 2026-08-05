#!/usr/bin/env python3
"""Conta óbitos por gripe (J09–J11) e dengue (A90/A91/A97) nos CSVs SIM em cache."""

from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

CACHE = Path("data_cache")
OUT = Path("data/sim_gripe_dengue_por_ano.json")


def classify(cid: str | None) -> str | None:
    if not cid:
        return None
    c = str(cid).strip().upper().replace(".", "")
    if c.startswith(("J09", "J10", "J11")):
        return "gripe"
    if c.startswith(("A90", "A91", "A97")):
        return "dengue"
    return None


def main():
    out = {}
    for path in sorted(CACHE.glob("DO*OPEN.csv")):
        year = 2000 + int(path.stem[2:4])
        counts: Counter = Counter()
        with open(path, "r", encoding="latin-1", newline="") as f:
            reader = csv.DictReader(f, delimiter=";")
            for row in reader:
                k = classify(row.get("CAUSABAS"))
                if k:
                    counts[k] += 1
        out[str(year)] = {
            "gripe": int(counts.get("gripe", 0)),
            "dengue": int(counts.get("dengue", 0)),
            "fonte": "SIM/DATASUS CAUSABAS",
            "evidencia": "ev-confirmed",
            "arquivo": path.name,
        }
        print(year, dict(out[str(year)]))

    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("salvo", OUT)


if __name__ == "__main__":
    main()
