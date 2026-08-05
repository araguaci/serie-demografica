#!/usr/bin/env python3
"""
brazil_deaths_by_age_2014_2025.py

Extensão do script original (brazil_deaths_by_age_2015_2024.py).

1. Janela 2014-2025, pivô em 2014 para colunas "Variação 14-XX".
2. 2014-2024: SIM/DATASUS oficial quando o arquivo OpenDataSUS existir.
   Anos sem CSV no S3 ficam marcados e podem ser preenchidos via seed.
3. 2025: Registro Civil (ARPEN) × fator SIM/RC do ano SIM_RC_CORRECTION_YEAR,
   distribuído pela estrutura etária do SIM nesse ano (metodologia WMD).
4. Proveniência ev-confirmed / ev-inference em proveniencia_2014_2025.json.
"""

from __future__ import annotations

import csv
import io
import json
import logging
from collections import Counter
from dataclasses import asdict, dataclass, field
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

PIVOT_YEAR = 2014
SIM_FINAL_LAST_YEAR = 2024
EXTENSION_YEAR = 2025
SIM_RC_CORRECTION_YEAR = 2023

FAIXAS_ETARIAS = [
    "0-4", "5-14", "15-19", "20-29", "30-39", "40-59", "60-79", "80+"
]

S3_BASE = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/"
RC_API = "https://transparencia.registrocivil.org.br/api/record/death"
CACHE_DIR = Path("data_cache")
OUT_CSV = Path("brazil_deaths_by_age_2014_2025.csv")
OUT_RATES_CSV = Path("brazil_death_rates_by_age_2014_2025.csv")
OUT_PROVENIENCIA = Path("proveniencia_2014_2025.json")
OUT_META = Path("brazil_deaths_by_age_2014_2025_meta.json")

# Taxas por 100 mil já publicadas no site (Tabela 2) — base para recalcular 2024/2025
SEED_RATES = {
    2014: {"0-4": 520.5, "5-14": 18.5, "15-19": 120.5, "20-29": 165.8,
           "30-39": 95.3, "40-59": 385.4, "60-79": 2420.5, "80+": 11850.2},
    2019: {"0-4": 485.8, "5-14": 15.2, "15-19": 115.2, "20-29": 158.3,
           "30-39": 92.1, "40-59": 388.7, "60-79": 2445.3, "80+": 11920.5},
    2020: {"0-4": 490.3, "5-14": 16.8, "15-19": 118.5, "20-29": 162.5,
           "30-39": 98.5, "40-59": 425.8, "60-79": 2850.2, "80+": 13250.8},
    2021: {"0-4": 495.2, "5-14": 17.2, "15-19": 120.8, "20-29": 168.5,
           "30-39": 105.2, "40-59": 485.3, "60-79": 3250.5, "80+": 14850.3},
    2023: {"0-4": 445.5, "5-14": 14.8, "15-19": 110.3, "20-29": 148.5,
           "30-39": 88.4, "40-59": 390.2, "60-79": 2470.8, "80+": 12050.3},
}


@dataclass
class FonteDados:
    ano: int
    fonte: str
    evidencia: str
    observacao: str = ""
    data_ingestao: str = field(default_factory=lambda: datetime.now().isoformat())


def get_fonte(ano: int) -> FonteDados:
    if ano <= SIM_FINAL_LAST_YEAR:
        return FonteDados(
            ano=ano,
            fonte="SIM/DATASUS",
            evidencia="ev-confirmed",
            observacao="Dado oficial (OpenDataSUS DO##OPEN.csv) quando disponível.",
        )
    return FonteDados(
        ano=ano,
        fonte="RC/ARPEN (corrigido)",
        evidencia="ev-inference",
        observacao=(
            f"SIM {ano} ainda não publicado (nem versão preliminar). "
            f"Estimado via Registro Civil, corrigido pelo fator SIM/RC "
            f"calculado em {SIM_RC_CORRECTION_YEAR}. Revisar quando o SIM "
            f"preliminar de {ano} sair."
        ),
    )


def sim_csv_url(ano: int) -> str:
    return f"{S3_BASE}DO{ano % 100:02d}OPEN.csv"


def sim_cache_path(ano: int) -> Path:
    return CACHE_DIR / f"DO{ano % 100:02d}OPEN.csv"


def sim_disponivel(ano: int) -> bool:
    path = sim_cache_path(ano)
    if path.exists() and path.stat().st_size > 1_000_000:
        return True
    try:
        r = requests.head(sim_csv_url(ano), timeout=20)
        return r.status_code == 200
    except requests.RequestException:
        return False


def baixar_sim_datasus(ano: int) -> Path:
    """Baixa DO##OPEN.csv do OpenDataSUS (S3) para cache local."""
    CACHE_DIR.mkdir(exist_ok=True)
    dest = sim_cache_path(ano)
    if dest.exists() and dest.stat().st_size > 1_000_000:
        log.info("Cache SIM %s: %s", ano, dest)
        return dest

    url = sim_csv_url(ano)
    log.info("Baixando SIM %s (SIM/DATASUS oficial)... %s", ano, url)
    with requests.get(url, stream=True, timeout=300) as r:
        r.raise_for_status()
        with open(dest, "wb") as f:
            for chunk in r.iter_content(chunk_size=8 * 1024 * 1024):
                if chunk:
                    f.write(chunk)
    log.info("SIM %s salvo (%s bytes)", ano, f"{dest.stat().st_size:,}")
    return dest


def idade_to_anos(val) -> int | None:
    """
    Decodifica IDADE do SIM.
    Empiricamente nos OPEN CSV: 4xx e 5xx = anos; 1/2/3xx = <1 ano.
    """
    try:
        v = int(float(str(val).strip()))
    except (TypeError, ValueError):
        return None
    if v in (0, 999) or v >= 900:
        return None
    unidade, q = divmod(v, 100)
    if unidade in (4, 5):
        return q
    if unidade in (1, 2, 3):
        return 0
    if v < 130:
        return v
    return None


def faixa_etaria(anos: int | None) -> str:
    if anos is None:
        return "ignorado"
    if anos <= 4:
        return "0-4"
    if anos <= 14:
        return "5-14"
    if anos <= 19:
        return "15-19"
    if anos <= 29:
        return "20-29"
    if anos <= 39:
        return "30-39"
    if anos <= 59:
        return "40-59"
    if anos <= 79:
        return "60-79"
    return "80+"


def processar_sim_arquivo(path: Path) -> dict:
    counts: Counter = Counter()
    n = 0
    with open(path, "r", encoding="latin-1", newline="") as f:
        reader = csv.DictReader(f, delimiter=";")
        if not reader.fieldnames or "IDADE" not in reader.fieldnames:
            raise ValueError(f"Coluna IDADE ausente em {path}")
        for row in reader:
            n += 1
            counts[faixa_etaria(idade_to_anos(row["IDADE"]))] += 1
            if n % 300_000 == 0:
                log.info("  %s: %s linhas", path.name, f"{n:,}")
    out = {k: int(counts.get(k, 0)) for k in FAIXAS_ETARIAS}
    out["ignorado"] = int(counts.get("ignorado", 0))
    out["Total_deaths"] = n
    return out


def baixar_registro_civil_total(ano: int) -> int:
    """Total nacional de óbitos no Portal da Transparência (ARPEN)."""
    params = {"start_date": f"{ano}-01-01", "end_date": f"{ano}-12-31"}
    headers = {"User-Agent": "serie-demografica/1.0", "Accept": "application/json"}
    log.info("Baixando Registro Civil (ARPEN) %s...", ano)
    r = requests.get(RC_API, params=params, headers=headers, timeout=60)
    r.raise_for_status()
    data = r.json().get("data") or []
    total = int(sum(item.get("total", 0) for item in data))
    log.info("RC %s total nacional: %s (%s UFs)", ano, f"{total:,}", len(data))
    return total


def calcular_fator_correcao(sim_total: int, rc_total: int) -> float:
    if rc_total == 0:
        raise ValueError("Total do Registro Civil não pode ser zero.")
    fator = sim_total / rc_total
    log.info(
        "Fator SIM/RC (%s): %.6f (SIM=%s, RC=%s)",
        SIM_RC_CORRECTION_YEAR, fator, f"{sim_total:,}", f"{rc_total:,}",
    )
    return fator


def estimar_ano_rc(
    total_corrigido: int,
    dist_ref: dict[str, int],
) -> dict:
    """Distribui o total corrigido pela estrutura etária de referência (SIM)."""
    known = sum(dist_ref.get(f, 0) for f in FAIXAS_ETARIAS)
    if known <= 0:
        raise ValueError("Distribuição de referência sem óbitos conhecidos.")
    out = {}
    acc = 0
    for i, f in enumerate(FAIXAS_ETARIAS):
        if i == len(FAIXAS_ETARIAS) - 1:
            out[f] = total_corrigido - acc
        else:
            val = round(total_corrigido * dist_ref[f] / known)
            out[f] = val
            acc += val
    out["ignorado"] = 0
    out["Total_deaths"] = total_corrigido
    return out


def recalcular_variacao(
    df: pd.DataFrame,
    ano_base: int = PIVOT_YEAR,
    ano_final: int = EXTENSION_YEAR,
) -> pd.DataFrame:
    if ano_base not in df.columns or ano_final not in df.columns:
        raise KeyError(
            f"Colunas {ano_base} e/ou {ano_final} ausentes. "
            f"Confirme ingestão {ano_base}-{ano_final}."
        )
    label = f"Variação {str(ano_base)[-2:]}-{str(ano_final)[-2:]}"
    df = df.copy()
    df[label] = ((df[ano_final] - df[ano_base]) / df[ano_base] * 100).round(1)
    return df


def taxas_a_partir_de_obitos(
    obitos_ano: dict[str, int],
    taxas_ref: dict[str, float],
    obitos_ref: dict[str, int],
) -> dict[str, float]:
    """
    Escala taxas de referência pela razão de óbitos absolutos
    (aproxima população estável entre os dois anos).
    """
    out = {}
    for f in FAIXAS_ETARIAS:
        base = obitos_ref.get(f) or 0
        if base <= 0:
            out[f] = round(taxas_ref[f], 1)
        else:
            out[f] = round(taxas_ref[f] * obitos_ano[f] / base, 1)
    return out


def montar_tabela_taxas(
    sim_anos: dict[int, dict],
    est_2025: dict,
) -> pd.DataFrame:
    rates = {ano: dict(vals) for ano, vals in SEED_RATES.items()}
    ref_obitos = {f: sim_anos[2023][f] for f in FAIXAS_ETARIAS}
    rates[2024] = taxas_a_partir_de_obitos(
        {f: sim_anos[2024][f] for f in FAIXAS_ETARIAS},
        SEED_RATES[2023],
        ref_obitos,
    )
    rates[2025] = taxas_a_partir_de_obitos(
        {f: est_2025[f] for f in FAIXAS_ETARIAS},
        SEED_RATES[2023],
        ref_obitos,
    )
    df = pd.DataFrame(rates).reindex(FAIXAS_ETARIAS)
    df.index.name = "Faixa Etária"
    return recalcular_variacao(df)


def main():
    log.info(
        "Montando série %s-%s (pivô %s; %s-%s SIM; %s RC corrigido)",
        PIVOT_YEAR, EXTENSION_YEAR, PIVOT_YEAR,
        PIVOT_YEAR, SIM_FINAL_LAST_YEAR, EXTENSION_YEAR,
    )
    CACHE_DIR.mkdir(exist_ok=True)

    registros: list[FonteDados] = []
    sim_anos: dict[int, dict] = {}

    # SIM disponível no S3 OpenDataSUS (hoje tipicamente 2022-2024)
    for ano in range(PIVOT_YEAR, SIM_FINAL_LAST_YEAR + 1):
        fonte = get_fonte(ano)
        if not sim_disponivel(ano):
            fonte.observacao = (
                f"Arquivo {sim_csv_url(ano)} indisponível no S3 neste momento. "
                "Ano omitido do CSV absoluto; taxas históricas do seed mantidas no site."
            )
            fonte.evidencia = "ev-inference"
            registros.append(fonte)
            log.warning("SIM %s indisponível no OpenDataSUS S3 — pulando download.", ano)
            continue
        path = baixar_sim_datasus(ano)
        sim_anos[ano] = processar_sim_arquivo(path)
        registros.append(fonte)
        log.info("SIM %s: %s óbitos", ano, f"{sim_anos[ano]['Total_deaths']:,}")

    if SIM_RC_CORRECTION_YEAR not in sim_anos:
        raise RuntimeError(
            f"Ano de correção {SIM_RC_CORRECTION_YEAR} sem dados SIM. "
            "Não é possível estimar 2025."
        )

    rc_correcao = baixar_registro_civil_total(SIM_RC_CORRECTION_YEAR)
    rc_2025 = baixar_registro_civil_total(EXTENSION_YEAR)
    fator = calcular_fator_correcao(
        sim_anos[SIM_RC_CORRECTION_YEAR]["Total_deaths"],
        rc_correcao,
    )
    total_2025 = round(rc_2025 * fator)
    est_2025 = estimar_ano_rc(
        total_2025,
        {f: sim_anos[SIM_RC_CORRECTION_YEAR][f] for f in FAIXAS_ETARIAS},
    )
    fonte_2025 = get_fonte(EXTENSION_YEAR)
    fonte_2025.observacao += (
        f" RC bruto={rc_2025:,}; fator={fator:.6f}; total corrigido={total_2025:,}."
    )
    registros.append(fonte_2025)

    # DataFrame absoluto (anos com microdado + 2025)
    rows = []
    for ano, data in sorted(sim_anos.items()):
        row = {"Year": ano, **{f: data[f] for f in FAIXAS_ETARIAS},
               "Total_deaths": data["Total_deaths"], "ignorado": data["ignorado"],
               "fonte": "SIM/DATASUS", "evidencia": "ev-confirmed"}
        rows.append(row)
    rows.append({
        "Year": EXTENSION_YEAR,
        **{f: est_2025[f] for f in FAIXAS_ETARIAS},
        "Total_deaths": est_2025["Total_deaths"],
        "ignorado": 0,
        "fonte": "RC/ARPEN (corrigido)",
        "evidencia": "ev-inference",
    })
    df_abs = pd.DataFrame(rows).sort_values("Year")
    df_abs.to_csv(OUT_CSV, index=False)
    log.info("CSV absoluto: %s", OUT_CSV)

    # Taxas (site) com variação 14-25
    df_rates = montar_tabela_taxas(sim_anos, est_2025)
    df_rates.to_csv(OUT_RATES_CSV)
    log.info("CSV taxas: %s", OUT_RATES_CSV)

    with open(OUT_PROVENIENCIA, "w", encoding="utf-8") as f:
        json.dump([asdict(r) for r in registros], f, ensure_ascii=False, indent=2)

    meta = {
        "gerado_em": datetime.now().isoformat(),
        "fator_sim_rc": fator,
        "sim_rc_correction_year": SIM_RC_CORRECTION_YEAR,
        "rc_correction_total": rc_correcao,
        "rc_2025_total": rc_2025,
        "estimativa_2025_total": total_2025,
        "anos_sim_processados": sorted(sim_anos.keys()),
        "variacao_label": f"Variação {str(PIVOT_YEAR)[-2:]}-{str(EXTENSION_YEAR)[-2:]}",
        "taxas": {
            str(c): {f: float(df_rates.loc[f, c]) for f in FAIXAS_ETARIAS}
            for c in df_rates.columns if str(c).isdigit()
        },
        "variacao_14_25": {
            f: float(df_rates.loc[f, f"Variação {str(PIVOT_YEAR)[-2:]}-{str(EXTENSION_YEAR)[-2:]}"])
            for f in FAIXAS_ETARIAS
        },
    }
    OUT_META.write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")

    confirmed = sum(1 for r in registros if r.evidencia == "ev-confirmed")
    inferred = sum(1 for r in registros if r.evidencia == "ev-inference")
    log.info(
        "Proveniência em %s — %s ev-confirmed, %s ev-inference.",
        OUT_PROVENIENCIA, confirmed, inferred,
    )
    print("\n=== Taxas (por 100 mil) — colunas-chave ===")
    cols = [c for c in [2014, 2023, 2024, 2025, "Variação 14-25"] if c in df_rates.columns]
    print(df_rates[cols].to_string())
    print("\n=== Óbitos absolutos (anos processados) ===")
    print(df_abs.to_string(index=False))


if __name__ == "__main__":
    main()
