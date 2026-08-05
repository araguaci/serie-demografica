#!/usr/bin/env python3
"""
extract_cancer_miocardite_sim.py

Conta óbitos por câncer e miocardite nos microdados SIM (OpenDataSUS)
em cache local (data_cache/DO##OPEN.csv).

CID-10 (causa básica CAUSABAS):
  - câncer / neoplasias malignas: C00–C97
  - miocardite aguda: I40
  - (opcional no breakdown) I41, I51.4

Uso:
  python extract_cancer_miocardite_sim.py

Saídas:
  data/sim_cancer_miocardite_por_ano.json   — só anos com microdado
  data/obitos_cancer_miocardite_2014_2025.json — atualiza anos SIM confirmados
"""

from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime
from pathlib import Path

CACHE = Path("data_cache")
OUT_SIM = Path("data/sim_cancer_miocardite_por_ano.json")
OUT_SERIE = Path("data/obitos_cancer_miocardite_2014_2025.json")

# Série histórica (TabNet / literatura) — preservada; anos SIM sobrescrevem
SEED_CANCER = {
    2014: 197929, 2015: 205584, 2016: 210913, 2017: 217385,
    2018: 223362, 2019: 230595, 2020: 224714, 2021: 231089,
}
SEED_MIO = {
    2014: 119, 2015: 130, 2016: 127, 2017: 127,
    2018: 118, 2019: 100, 2020: 120, 2021: 158,
}


def normalize_cid(cid: str | None) -> str:
    if not cid:
        return ""
    return str(cid).strip().upper().replace(".", "")


def is_cancer(cid: str) -> bool:
    if len(cid) < 3 or cid[0] != "C":
        return False
    try:
        return 0 <= int(cid[1:3]) <= 97
    except ValueError:
        return False


def mio_bucket(cid: str) -> str | None:
    if cid.startswith("I40"):
        return "I40"
    if cid.startswith("I41"):
        return "I41"
    if cid.startswith("I514"):
        return "I514"
    return None


def process_file(path: Path) -> dict:
    cancer = 0
    mio = Counter()
    total = 0
    with open(path, "r", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if not reader.fieldnames or "CAUSABAS" not in reader.fieldnames:
            raise ValueError(f"Coluna CAUSABAS ausente em {path}")
        for row in reader:
            total += 1
            cid = normalize_cid(row.get("CAUSABAS"))
            if is_cancer(cid):
                cancer += 1
            bucket = mio_bucket(cid)
            if bucket:
                mio[bucket] += 1
            if total % 300_000 == 0:
                print(f"  {path.name}: {total:,} linhas", flush=True)
    i40 = int(mio.get("I40", 0))
    return {
        "cancer_C00_C97": cancer,
        "miocardite_I40": i40,
        "miocardite_I41": int(mio.get("I41", 0)),
        "miocardite_I514": int(mio.get("I514", 0)),
        "miocardite_I40_I41_I514": i40 + int(mio.get("I41", 0)) + int(mio.get("I514", 0)),
        "total_registros": total,
        "fonte": "SIM/DATASUS CAUSABAS",
        "evidencia": "ev-confirmed",
        "arquivo": path.name,
    }


def merge_serie(sim_anos: dict[str, dict]) -> dict:
    """Monta série 2014–2025: seed + SIM; 2025 estimado se houver 2024."""
    anos = list(range(2014, 2026))
    cancer: dict[int, int] = dict(SEED_CANCER)
    mio: dict[int, int] = dict(SEED_MIO)
    cancer_meta = []
    mio_meta = []

    for ano in range(2014, 2022):
        cancer_meta.append({
            "ano": ano,
            "evidencia": "ev-surveillance",
            "fonte": "TabNet Cap.II ×0,98 (Monteiro et al. 2025)",
        })
        mio_meta.append({
            "ano": ano,
            "evidencia": "ev-surveillance",
            "fonte": "DATASUS I40 (série publicada 2014–2023)",
        })

    for ys, row in sorted(sim_anos.items()):
        ano = int(ys)
        cancer[ano] = int(row["cancer_C00_C97"])
        mio[ano] = int(row["miocardite_I40"])

    for ano in sorted(int(y) for y in sim_anos):
        cancer_meta.append({
            "ano": ano,
            "evidencia": "ev-confirmed",
            "fonte": "SIM/DATASUS CAUSABAS C00–C97",
        })
        mio_meta.append({
            "ano": ano,
            "evidencia": "ev-confirmed",
            "fonte": "SIM/DATASUS CAUSABAS I40",
        })

    # 2025: estimativa simples se houver 2024 e totais no meta do pipeline
    if 2024 in cancer and 2025 not in sim_anos:
        meta_path = Path("brazil_deaths_by_age_2014_2025_meta.json")
        if meta_path.exists():
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
            t24 = None
            # total SIM 2024 dos anos processados
            for ys, row in sim_anos.items():
                if int(ys) == 2024:
                    t24 = row.get("total_registros")
            t25 = meta.get("estimativa_2025_total")
            if t24 and t25:
                cancer[2025] = round(cancer[2024] * t25 / t24)
                mio[2025] = round(mio[2024] * t25 / t24)
                cancer_meta.append({
                    "ano": 2025,
                    "evidencia": "ev-inference",
                    "fonte": "Câncer 2024 × razão totais RC corrigido / SIM 2024",
                })
                mio_meta.append({
                    "ano": 2025,
                    "evidencia": "ev-inference",
                    "fonte": "I40 2024 × razão totais RC corrigido / SIM 2024",
                })

    cancer_meta.sort(key=lambda x: x["ano"])
    mio_meta.sort(key=lambda x: x["ano"])

    return {
        "periodo": "2014-2025",
        "atualizado_em": datetime.now().date().isoformat(),
        "notas": [
            "Câncer (C00–C97): anos com DO##OPEN.csv = SIM confirmado; "
            "2014–2021 = neoplasias Cap. II × 0,98 (Monteiro et al. 2025).",
            "Miocardite aguda (I40): 2014–2021 série DATASUS publicada; "
            "anos com microdado = SIM I40. Não inclui I51.4 por padrão.",
            "Rode: python extract_cancer_miocardite_sim.py",
        ],
        "anos": anos,
        "cancer": [cancer.get(a) for a in anos],
        "cancer_meta": cancer_meta,
        "miocardite": [mio.get(a) for a in anos],
        "miocardite_meta": mio_meta,
        "neoplasias_cap2_tabnet": {
            "2014": 201968, "2015": 209780, "2016": 215217, "2017": 221821,
            "2018": 227920, "2019": 235301, "2020": 229300, "2021": 235805,
            "2022": 244009, "2023": 255037,
        },
    }


def main():
    files = sorted(CACHE.glob("DO*OPEN.csv"))
    if not files:
        raise SystemExit(
            f"Nenhum {CACHE}/DO*OPEN.csv encontrado. "
            "Baixe antes com brazil_deaths_by_age_2014_2025.py"
        )

    sim_anos: dict[str, dict] = {}
    for path in files:
        year = 2000 + int(path.stem[2:4])
        print(f"Processando SIM {year} ({path.name})...", flush=True)
        row = process_file(path)
        sim_anos[str(year)] = row
        print(
            f"  câncer={row['cancer_C00_C97']:,}  "
            f"I40={row['miocardite_I40']:,}  "
            f"I514={row['miocardite_I514']:,}  "
            f"total={row['total_registros']:,}",
            flush=True,
        )

    OUT_SIM.parent.mkdir(exist_ok=True)
    OUT_SIM.write_text(
        json.dumps(sim_anos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("salvo", OUT_SIM)

    serie = merge_serie(sim_anos)
    OUT_SERIE.write_text(
        json.dumps(serie, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print("salvo", OUT_SERIE)


if __name__ == "__main__":
    main()
