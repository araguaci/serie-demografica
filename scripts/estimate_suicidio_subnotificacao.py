#!/usr/bin/env python3
"""
estimate_suicidio_subnotificacao.py

Modelo de três camadas para subnotificação de suicídio (X60–X84 vs Y10–Y34):

  piso     = X60–X84                          (ev-confirmed)
  central  = X60–X84 + (Y10–Y34 × fator)      (ev-inference)
  teto     = X60–X84 + Y10–Y34                (limite teórico)

Fator default 0,35 (faixa literatura 0,20–0,45). Ver docs/NOTA-SUBNOTIFICACAO.md.

Uso:
  python extract_suicidio_sim.py          # gera data/sim_suicidio_por_ano.json
  python scripts/estimate_suicidio_subnotificacao.py
  python scripts/estimate_suicidio_subnotificacao.py --fator 0.35
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SIM_PATH = ROOT / "data" / "sim_suicidio_por_ano.json"
SERIE_PATH = ROOT / "data" / "obitos_suicidio_2005_2025.json"
OUT_PATH = ROOT / "data" / "obitos_suicidio_subnotificacao.json"

FATOR_DEFAULT = 0.35
FATOR_MIN = 0.20
FATOR_MAX = 0.45


def layers(x60: int, y10: int, fator: float) -> dict:
    piso = int(x60)
    teto = int(x60) + int(y10)
    central = round(piso + y10 * fator)
    denom = piso + y10
    taxa = round(100.0 * y10 / denom, 2) if denom else None
    return {
        "piso_X60_X84": piso,
        "indeterminado_Y10_Y34": int(y10),
        "central_estimado": central,
        "teto_X60_Y34": teto,
        "fator_realocacao": fator,
        "taxa_indeterminacao_pct": taxa,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--fator",
        type=float,
        default=FATOR_DEFAULT,
        help=f"Fator de realocação Y10–Y34→suicídio (default {FATOR_DEFAULT})",
    )
    args = ap.parse_args()
    fator = max(FATOR_MIN, min(FATOR_MAX, args.fator))
    if fator != args.fator:
        print(f"AVISO: fator {args.fator} clampado para {fator} (faixa {FATOR_MIN}–{FATOR_MAX})")

    if not SIM_PATH.exists():
        raise SystemExit(f"Falta {SIM_PATH} — rode: python extract_suicidio_sim.py")

    sim = json.loads(SIM_PATH.read_text(encoding="utf-8"))
    serie_seed = {}
    if SERIE_PATH.exists():
        serie = json.loads(SERIE_PATH.read_text(encoding="utf-8"))
        for a, v in zip(serie.get("anos", []), serie.get("suicidio", [])):
            if v is not None:
                serie_seed[int(a)] = int(v)

    por_ano = {}
    for ys, row in sorted(sim.items()):
        ano = int(ys)
        x60 = int(row["suicidio_X60_X84"])
        y10 = int(row.get("indeterminado_Y10_Y34") or 0)
        if "indeterminado_Y10_Y34" not in row:
            raise SystemExit(
                f"{SIM_PATH}: ano {ano} sem indeterminado_Y10_Y34 — "
                "reexecute extract_suicidio_sim.py com o contador Y10–Y34."
            )
        L = layers(x60, y10, fator)
        por_ano[str(ano)] = {
            **L,
            "maturacao": "maduro",
            "tag_painel": "ok",
            "evidencia_piso": "ev-confirmed",
            "evidencia_central": "ev-inference",
            "fonte": row.get("fonte", "SIM/DATASUS CAUSABAS"),
            "arquivo": row.get("arquivo"),
        }

    # Comparativo de taxa (teste 1 da investigação)
    taxas = {
        int(a): por_ano[a]["taxa_indeterminacao_pct"]
        for a in por_ano
        if por_ano[a]["taxa_indeterminacao_pct"] is not None
    }
    hipotese = None
    if len(taxas) >= 2:
        anos_sim = sorted(taxas)
        ultimo = anos_sim[-1]
        anteriores = anos_sim[:-1]
        ok = all(taxas[ultimo] > taxas[a] for a in anteriores)
        hipotese = {
            "teste": f"taxa_indeterminacao_{ultimo} > anos SIM anteriores",
            "resultado": "confirmado" if ok else "nao_confirmado",
            "taxas_pct": {str(k): v for k, v in sorted(taxas.items())},
            "interpretacao": (
                f"Lag de fechamento compatível: {ultimo} tem mais Y10–Y34 relativo "
                f"({taxas[ultimo]}%) que {anteriores}. A queda do piso X60–X84 "
                "não deve ser lida como redução real de suicídios; use a faixa "
                "piso–central–teto."
                if ok
                else "Taxa de indeterminação do ano mais recente não supera os "
                "anteriores; revisar hipótese ou qualidade do microdado."
            ),
        }
        if ok:
            por_ano[str(ultimo)]["maturacao"] = "provisorio"
            por_ano[str(ultimo)]["tag_painel"] = "ok-provisorio"

    # Série longa: anos sem Y10 usam piso=central=teto (seed)
    anos = list(range(2005, 2026))
    piso, central, teto, tags, meta = [], [], [], [], []
    for ano in anos:
        key = str(ano)
        if key in por_ano:
            r = por_ano[key]
            piso.append(r["piso_X60_X84"])
            central.append(r["central_estimado"])
            teto.append(r["teto_X60_Y34"])
            tag = r.get("tag_painel") or ("ok-provisorio" if r["maturacao"] == "provisorio" else "ok")
            tags.append(tag)
            meta.append({
                "ano": ano,
                "evidencia": "ev-confirmed" if tag == "ok" else "ev-inference",
                "fonte": f"SIM X60–X84 + Y10–Y34 (fator {fator})",
                "maturacao": r["maturacao"],
                "taxa_indeterminacao_pct": r["taxa_indeterminacao_pct"],
            })
        elif ano == 2025 and "2024" in por_ano:
            # Extrapolação sobre central 2024 × fator RC (se disponível)
            meta_path = ROOT / "brazil_deaths_by_age_2014_2025_meta.json"
            c24 = por_ano["2024"]["central_estimado"]
            p24 = por_ano["2024"]["piso_X60_X84"]
            t24 = por_ano["2024"]["teto_X60_Y34"]
            ratio = 1.0
            if meta_path.exists():
                pipe = json.loads(meta_path.read_text(encoding="utf-8"))
                tot24 = por_ano["2024"].get("arquivo") and sim["2024"].get("total_registros")
                tot25 = pipe.get("estimativa_2025_total")
                if tot24 and tot25:
                    ratio = tot25 / tot24
            piso.append(round(p24 * ratio))
            central.append(round(c24 * ratio))
            teto.append(round(t24 * ratio))
            tags.append("inf")
            meta.append({
                "ano": 2025,
                "evidencia": "ev-inference",
                "fonte": f"Camadas 2024 × razão RC 2025 (fator {fator})",
                "maturacao": "estimado",
            })
        else:
            v = serie_seed.get(ano)
            piso.append(v)
            central.append(v)
            teto.append(v)
            tags.append("gap")
            meta.append({
                "ano": ano,
                "evidencia": "ev-surveillance",
                "fonte": "Seed TabNet/boletim — sem Y10–Y34 neste pipeline",
                "maturacao": "seed",
            })

    out = {
        "periodo": "2005-2025",
        "atualizado_em": datetime.now(timezone.utc).date().isoformat(),
        "modelo": {
            "piso": "X60–X84",
            "central": f"X60–X84 + (Y10–Y34 × {fator})",
            "teto": "X60–X84 + Y10–Y34",
            "fator_realocacao": fator,
            "fator_faixa_literatura": [FATOR_MIN, FATOR_MAX],
            "nota": (
                "Óbitos confirmados (X60–X84) subestimam o total real de suicídios devido "
                "a eventos ainda classificados como intenção indeterminada (Y10–Y34). "
                "A faixa piso–teto reflete essa incerteza; o valor central usa fator de "
                "realocação de literatura (ev-inference), não um dado direto do SIM."
            ),
        },
        "hipotese_lag_fechamento": hipotese,
        "anos": anos,
        "piso": piso,
        "central": central,
        "teto": teto,
        "tags": tags,
        "meta": meta,
        "sim_anos": por_ano,
        "referencias": [
            "docs/NOTA-SUBNOTIFICACAO.md",
            "docs/INVESTIGACAO-SUBNOTIFICACAO.md",
        ],
    }

    OUT_PATH.parent.mkdir(exist_ok=True)
    OUT_PATH.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    print("salvo", OUT_PATH)
    print(f"fator={fator}")
    if hipotese:
        print("hipótese:", hipotese["resultado"], hipotese["taxas_pct"])
    for a, p, c, t, tag in zip(anos, piso, central, teto, tags):
        if a >= 2022 or a == 2021:
            print(f"  {a}: piso={p}  central={c}  teto={t}  [{tag}]")


if __name__ == "__main__":
    main()
