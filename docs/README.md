# Documentação — Série Demográfica

Índice da documentação técnica e metodológica do observatório
([serie-demografica.vercel.app](https://serie-demografica.vercel.app)).

**Versão do projeto:** ver [`../VERSION`](../VERSION) · histórico em [`../CHANGELOG.md`](../CHANGELOG.md)

---

## Operacional

| Documento | Conteúdo |
|-----------|----------|
| [EXTRACAO-DADOS.md](EXTRACAO-DADOS.md) | Pipeline: download SIM, RC/ARPEN, extractors, tags de evidência, troubleshooting |

## Suicídio e subnotificação

| Documento | Conteúdo |
|-----------|----------|
| [NOTA-SUBNOTIFICACAO.md](NOTA-SUBNOTIFICACAO.md) | Modelo piso / central / teto (X60–X84 vs Y10–Y34); texto de rodapé do gráfico |
| [INVESTIGACAO-SUBNOTIFICACAO.md](INVESTIGACAO-SUBNOTIFICACAO.md) | Investigação do gap 2024; teste de lag de fechamento (**confirmado**) |

## Dados versionados (`data/`)

| Arquivo | Descrição |
|---------|-----------|
| `obitos_gripe_dengue_2016_2025.json` | Dengue SVS + gripe SIM |
| `obitos_cancer_miocardite_2014_2025.json` | Câncer C00–C97 + miocardite I40 |
| `obitos_suicidio_2005_2025.json` | Piso X60–X84 (série longa) |
| `obitos_suicidio_subnotificacao.json` | Piso / central / teto + taxas Y10–Y34 |
| `sim_*_por_ano.json` | Contagens brutas por ano com microdado em cache |

## Scripts relacionados

```bash
python extract_suicidio_sim.py
python scripts/estimate_suicidio_subnotificacao.py
# opcional / exploratório:
# python scripts/estimate_suicidio_subnotificacao_uf.py
# python scripts/correlate_subnotificacao_insolvencia.py
```

## Ajuda (sempre visível no painel)

Em sofrimento psíquico: **CVV 188** · [cvv.org.br](https://www.cvv.org.br) · SAMU **192**
