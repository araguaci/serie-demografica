#!/usr/bin/env python3
"""
correlate_subnotificacao_insolvencia.py

Template para testar a hipótese: "UFs com maior estresse socioeconômico
(medido por taxa de recuperação judicial de micro/pequenas empresas)
têm maior taxa de indeterminação (Y10-Y34) na classificação de suicídio?"

IMPORTANTE — isso é um teste de hipótese, não uma conclusão pré-formatada.
Correlação aqui não implica causalidade, e o próprio dataset de insolvência
já tem uma ressalva conhecida (JOTA aponta viés paternalista do judiciário
inflando números de RJ agro em algumas UFs) — reporte isso junto de
qualquer resultado.

Requer dois inputs:
  1. ranking_uf_2019_2024 (saída de estimate_suicidio_subnotificacao_uf.py)
  2. seu dataset de insolvência por UF (recuperações judiciais / 2024,
     Q1 2026), no formato ['uf', 'rj_taxa_100k_empresas'] ou equivalente —
     ajuste os nomes de coluna conforme o que você já tem salvo.

Uso:
  python correlate_subnotificacao_insolvencia.py \
      --suicidio data/suicidio_subnotificacao_por_uf.json \
      --insolvencia data/insolvencia_por_uf.csv \
      --output data/correlacao_subnotificacao_insolvencia.json
"""

import argparse
import json
from pathlib import Path

import pandas as pd
from scipy import stats


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--suicidio", required=True, help="JSON de estimate_suicidio_subnotificacao_uf.py")
    ap.add_argument("--insolvencia", required=True, help="CSV com colunas ['uf', <métrica RJ>]")
    ap.add_argument("--insolvencia-col", default="rj_taxa_100k_empresas")
    ap.add_argument("--output", required=True)
    args = ap.parse_args()

    with open(args.suicidio, "r", encoding="utf-8") as f:
        suic = json.load(f)
    ranking = pd.DataFrame(suic["ranking_uf_2019_2024"])

    insolv = pd.read_csv(args.insolvencia)
    if "uf" not in insolv.columns or args.insolvencia_col not in insolv.columns:
        raise ValueError(
            f"Esperado colunas ['uf', '{args.insolvencia_col}'] em {args.insolvencia}"
        )

    merged = ranking.merge(insolv[["uf", args.insolvencia_col]], on="uf", how="inner")

    if len(merged) < 5:
        print(f"Aviso: apenas {len(merged)} UFs cruzadas — amostra pequena para correlação.")

    r, p = stats.pearsonr(
        merged["taxa_indeterminacao_pct"], merged[args.insolvencia_col]
    )
    rho, p_rho = stats.spearmanr(
        merged["taxa_indeterminacao_pct"], merged[args.insolvencia_col]
    )

    payload = {
        "n_uf": len(merged),
        "pearson_r": round(r, 3),
        "pearson_p": round(p, 4),
        "spearman_rho": round(rho, 3),
        "spearman_p": round(p_rho, 4),
        "leitura": (
            "Correlação exploratória entre taxa de indeterminação Y10-Y34 "
            "(proxy de subnotificação de suicídio) e estresse de "
            "insolvência de micro/pequenas empresas por UF. "
            "NÃO implica causalidade; considerar confundidores "
            "(cobertura de IML por UF, PIB per capita, urbanização). "
            "Dataset de insolvência tem viés conhecido (JOTA: "
            "comportamento judicial paternalista pode inflar RJ agro "
            "em algumas UFs)."
        ),
        "evidencia": "ev-inference — hipótese exploratória",
        "dados": merged.to_dict(orient="records"),
    }

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"n={len(merged)}  pearson_r={r:.3f} (p={p:.4f})  spearman_rho={rho:.3f} (p={p_rho:.4f})")
    print(f"-> {args.output}")


if __name__ == "__main__":
    main()
