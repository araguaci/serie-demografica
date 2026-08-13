#!/usr/bin/env python3
"""
extract_suicidio_sim.py

Conta óbitos por lesões autoprovocadas intencionalmente (suicídio)
nos microdados SIM em cache (data_cache/DO##OPEN.csv).

CID-10 (causa básica CAUSABAS):
  - X60–X84  lesões autoprovocadas intencionalmente
  - Y870     sequelas de lesões autoprovocadas (opcional no breakdown)

Uso:
  python extract_suicidio_sim.py

Saídas:
  data/sim_suicidio_por_ano.json
  data/obitos_suicidio_2005_2025.json  — série ~20 anos (seed + SIM)
"""

from __future__ import annotations

import csv
import json
from datetime import datetime, timezone
from pathlib import Path

CACHE = Path("data_cache")
OUT_SIM = Path("data/sim_suicidio_por_ano.json")
OUT_SERIE = Path("data/obitos_suicidio_2005_2025.json")

# Série de vigilância / TabNet (SIM nacional, causa básica X60–X84).
# Anos com microdado OpenDataSUS no cache sobrescrevem com ev-confirmed.
# Fontes típicas: MS/DATASUS TabNet, boletins e literatura que citam SIM.
# Valores alinhados a TabNet/SIM citados em literatura e boletim MS
# (X60–X84; 2021 = 15.507 no Boletim Epidemiológico v.55 n.04 / MS).
SEED_SUICIDIO = {
    2005: 8558,
    2006: 8639,
    2007: 8868,
    2008: 9328,
    2009: 9374,
    2010: 9454,
    2011: 9851,
    2012: 10321,
    2013: 10533,
    2014: 11121,
    2015: 11738,
    2016: 11433,
    2017: 12495,
    2018: 12733,
    2019: 13523,
    2020: 13837,
    2021: 15507,
}


def normalize_cid(cid: str | None) -> str:
    if not cid:
        return ""
    return str(cid).strip().upper().replace(".", "")


def is_suicide(cid: str) -> bool:
    """X60–X84 (3 primeiros chars X60…X84)."""
    if len(cid) < 3 or cid[0] != "X":
        return False
    try:
        n = int(cid[1:3])
    except ValueError:
        return False
    return 60 <= n <= 84


def is_sequela(cid: str) -> bool:
    return cid.startswith("Y870")


def process_file(path: Path) -> dict:
    suicidio = 0
    sequela = 0
    total = 0
    with open(path, "r", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if not reader.fieldnames or "CAUSABAS" not in reader.fieldnames:
            raise ValueError(f"Coluna CAUSABAS ausente em {path}")
        for row in reader:
            total += 1
            cid = normalize_cid(row.get("CAUSABAS"))
            if is_suicide(cid):
                suicidio += 1
            elif is_sequela(cid):
                sequela += 1
            if total % 300_000 == 0:
                print(f"  {path.name}: {total:,} linhas", flush=True)
    return {
        "suicidio_X60_X84": suicidio,
        "sequela_Y870": sequela,
        "total_registros": total,
        "fonte": "SIM/DATASUS CAUSABAS",
        "evidencia": "ev-confirmed",
        "arquivo": path.name,
    }


def merge_serie(sim_anos: dict[str, dict]) -> dict:
    anos = list(range(2005, 2026))
    vals: dict[int, int] = dict(SEED_SUICIDIO)
    meta: list[dict] = []

    for ano in sorted(SEED_SUICIDIO):
        fonte = (
            "MS Boletim Epidemiológico v.55 n.04 (SIM X60–X84/Y87.0)"
            if ano == 2021
            else "SIM/DATASUS TabNet X60–X84 (série publicada / literatura)"
        )
        meta.append({
            "ano": ano,
            "evidencia": "ev-surveillance",
            "fonte": fonte,
        })

    for ys, row in sorted(sim_anos.items()):
        ano = int(ys)
        vals[ano] = int(row["suicidio_X60_X84"])
        # remove seed meta for that year, add confirmed
        meta = [m for m in meta if m["ano"] != ano]
        meta.append({
            "ano": ano,
            "evidencia": "ev-confirmed",
            "fonte": "SIM/DATASUS CAUSABAS X60–X84",
        })

    # 2025: estimativa proporcional se houver 2024 + meta do pipeline
    if 2024 in vals and 2025 not in sim_anos:
        meta_path = Path("brazil_deaths_by_age_2014_2025_meta.json")
        t24 = None
        for ys, row in sim_anos.items():
            if int(ys) == 2024:
                t24 = row.get("total_registros")
        if meta_path.exists() and t24:
            pipe = json.loads(meta_path.read_text(encoding="utf-8"))
            t25 = pipe.get("estimativa_2025_total")
            if t25:
                vals[2025] = round(vals[2024] * t25 / t24)
                meta.append({
                    "ano": 2025,
                    "evidencia": "ev-inference",
                    "fonte": "Proporção SIM 2024 × estimativa total RC 2025",
                })

    meta.sort(key=lambda m: m["ano"])
    serie = [vals.get(a) for a in anos]
    return {
        "periodo": "2005-2025",
        "atualizado_em": datetime.now(timezone.utc).date().isoformat(),
        "cid": "X60–X84",
        "notas": [
            "Suicídio: causa básica CID-10 X60–X84 (lesões autoprovocadas intencionalmente).",
            "Anos com DO##OPEN.csv no cache = SIM confirmado; demais = seed de vigilância TabNet/literatura.",
            "2025 = estimativa proporcional quando SIM ainda não publicado.",
            "Este painel é epidemiológico. Em crise emocional: CVV 188 (https://www.cvv.org.br).",
        ],
        "anos": anos,
        "suicidio": serie,
        "suicidio_meta": meta,
        "ajuda": {
            "cvv": {
                "nome": "CVV — Centro de Valorização da Vida",
                "telefone": "188",
                "url": "https://www.cvv.org.br",
                "nota": "Apoio emocional 24h, gratuito e sigiloso",
            },
            "samu": {"nome": "SAMU", "telefone": "192"},
            "caps": {
                "nome": "CAPS / UBS",
                "url": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-mental",
            },
        },
        "referencias": [
            {
                "titulo": "DATASUS TabNet — Mortalidade (CID-10)",
                "url": "http://tabnet.datasus.gov.br/cgi/deftohtm.exe?sim/cnv/obt10uf.def",
            },
            {
                "titulo": "OpenDataSUS — microdados SIM",
                "url": "https://opendatasus.saude.gov.br/dataset/sim",
            },
            {
                "titulo": "OMS — Suicide (prevenção)",
                "url": "https://www.who.int/health-topics/suicide",
            },
            {
                "titulo": "MS — Saúde mental",
                "url": "https://www.gov.br/saude/pt-br/assuntos/saude-de-a-a-z/s/saude-mental",
            },
            {
                "titulo": "Setembro Amarelo — CVV",
                "url": "https://www.cvv.org.br/setembro-amarelo/",
            },
        ],
    }


def main() -> None:
    sim_anos: dict[str, dict] = {}
    files = sorted(CACHE.glob("DO*OPEN.csv"))
    if not files:
        print("AVISO: nenhum DO##OPEN.csv em data_cache/ — gerando só seed.")
    for path in files:
        year = 2000 + int(path.stem[2:4])
        print(f"processando {path.name} ({year})...", flush=True)
        sim_anos[str(year)] = process_file(path)
        print(year, sim_anos[str(year)], flush=True)

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
    for a, v in zip(serie["anos"], serie["suicidio"]):
        print(f"  {a}: {v}")


if __name__ == "__main__":
    main()
