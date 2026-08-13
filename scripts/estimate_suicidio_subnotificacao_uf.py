#!/usr/bin/env python3
"""
estimate_suicidio_subnotificacao_uf.py

Extensão de estimate_suicidio_subnotificacao.py: mesma lógica piso/central/teto,
mas quebrada por UF, para expor o viés regional de subnotificação (hipótese:
UFs com menor cobertura de perícia forense têm taxa de indeterminação
Y10-Y34 maior -> suicídio mais subestimado nessas UFs).

Requer que o microdado tenha coluna de UF de residência/ocorrência
(no SIM: 'codmunres' ou 'ufres' — ajuste UF_COL abaixo conforme seu
extract_suicidio_sim.py já expõe).

Uso:
  python estimate_suicidio_subnotificacao_uf.py \
      --input data/sim_causabas_uf_2005_2025.csv \
      --output data/suicidio_subnotificacao_por_uf.json \
      --fator 0.35

Saída: JSON com série por (ano, uf), mais um resumo consolidado por UF
(taxa média de indeterminação 2019-2024) pronto para ranking / mapa.
"""

import argparse
import json
import sys
from pathlib import Path

import pandas as pd

FATOR_REALOCACAO_DEFAULT = 0.35
CID_SUICIDIO = [f"X{n}" for n in range(60, 85)]
CID_INDETERMINADO = [f"Y{n}" for n in range(10, 35)]

# Ajuste este nome se sua extração usa outro rótulo de coluna para UF.
UF_COL_CANDIDATES = ["uf", "ufres", "sigla_uf", "codufres"]


def cid_prefix_in(causabas: str, prefixes: list[str]) -> bool:
    if not isinstance(causabas, str) or len(causabas) < 3:
        return False
    return causabas[:3] in prefixes


def find_uf_col(df: pd.DataFrame) -> str:
    for c in UF_COL_CANDIDATES:
        if c in df.columns:
            return c
    raise ValueError(
        f"Nenhuma coluna de UF encontrada. Esperado uma de: {UF_COL_CANDIDATES}. "
        "Ajuste UF_COL_CANDIDATES ou renomeie a coluna na extração."
    )


def load_and_aggregate(path: str) -> pd.DataFrame:
    df = pd.read_csv(path)

    if {"ano", "uf", "x60_x84", "y10_y34"}.issubset(df.columns):
        return df[["ano", "uf", "x60_x84", "y10_y34"]].copy()

    if not {"ano", "causabas"}.issubset(df.columns):
        raise ValueError("CSV precisa ter ['ano','causabas', <col UF>] no microdado.")

    uf_col = find_uf_col(df)
    df["is_suicidio"] = df["causabas"].apply(lambda c: cid_prefix_in(c, CID_SUICIDIO))
    df["is_indeterminado"] = df["causabas"].apply(
        lambda c: cid_prefix_in(c, CID_INDETERMINADO)
    )

    agg = (
        df.groupby(["ano", uf_col])
        .agg(x60_x84=("is_suicidio", "sum"), y10_y34=("is_indeterminado", "sum"))
        .reset_index()
        .rename(columns={uf_col: "uf"})
    )
    return agg


def build_estimates(agg: pd.DataFrame, fator: float) -> pd.DataFrame:
    agg = agg.sort_values(["uf", "ano"]).reset_index(drop=True)
    agg["piso_confirmado"] = agg["x60_x84"]
    agg["teto_maximo"] = agg["x60_x84"] + agg["y10_y34"]
    agg["central_estimado"] = agg["x60_x84"] + agg["y10_y34"] * fator
    agg["taxa_indeterminacao_pct"] = (
        agg["y10_y34"] / agg["teto_maximo"].replace(0, pd.NA) * 100
    ).round(2)
    return agg


def build_uf_ranking(agg: pd.DataFrame, ano_min: int = 2019, ano_max: int = 2024) -> pd.DataFrame:
    """Resumo: taxa média de indeterminação por UF na janela mais estável
    (2019-2024), para ranking/mapa — a métrica central da hipótese de viés
    regional."""
    janela = agg[(agg["ano"] >= ano_min) & (agg["ano"] <= ano_max)]
    resumo = (
        janela.groupby("uf")
        .agg(
            x60_x84_total=("x60_x84", "sum"),
            y10_y34_total=("y10_y34", "sum"),
        )
        .reset_index()
    )
    resumo["taxa_indeterminacao_pct"] = (
        resumo["y10_y34_total"]
        / (resumo["x60_x84_total"] + resumo["y10_y34_total"]).replace(0, pd.NA)
        * 100
    ).round(2)
    return resumo.sort_values("taxa_indeterminacao_pct", ascending=False)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--fator", type=float, default=FATOR_REALOCACAO_DEFAULT)
    args = ap.parse_args()

    if not Path(args.input).exists():
        print(f"Erro: {args.input} não encontrado.", file=sys.stderr)
        sys.exit(1)

    agg = load_and_aggregate(args.input)
    series = build_estimates(agg, args.fator)
    ranking = build_uf_ranking(series)

    payload = {
        "metodo": f"X60-X84 + Y10-Y34 x fator={args.fator}, quebrado por UF",
        "evidencia": {
            "piso_confirmado": "ev-confirmed",
            "central_estimado": "ev-inference",
            "ranking_uf": "ev-inference — hipótese de viés regional, não conclusão",
        },
        "series_por_uf_ano": series.to_dict(orient="records"),
        "ranking_uf_2019_2024": ranking.to_dict(orient="records"),
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"OK -> {args.output}")
    print("\nTop 10 UFs por taxa de indeterminação (2019-2024):")
    print(ranking.head(10).to_string(index=False))


if __name__ == "__main__":
    main()
