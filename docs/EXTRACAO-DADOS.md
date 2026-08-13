# Download e extração de dados

Guia operacional do pipeline **série-demografica**: baixar microdados SIM, consultar Registro Civil e gerar agregados usados no dashboard.

## Visão geral

```
OpenDataSUS (S3) ──► data_cache/DO##OPEN.csv ──► scripts de extração
                              │
ARPEN (API RC) ───────────────┼──► totais / fator SIM-RC / 2025
                              │
                              ▼
                    CSV / JSON em data/ e raiz
                              │
                              ▼
                         index.html (dashboard)
```

| Etapa | Script | Entrada | Saída principal |
|-------|--------|---------|-----------------|
| 1. Série etária + RC | `brazil_deaths_by_age_2014_2025.py` | S3 SIM + API ARPEN | CSV etário, taxas, proveniência, `data_cache/` |
| 2. Gripe / dengue | `extract_gripe_dengue_sim.py` | `data_cache/` | `data/sim_gripe_dengue_por_ano.json` |
| 3. Câncer / miocardite | `extract_cancer_miocardite_sim.py` | `data_cache/` | `data/sim_cancer_miocardite_por_ano.json` + série 2014–2025 |
| 4. Suicídio | `extract_suicidio_sim.py` | `data_cache/` | `data/sim_suicidio_por_ano.json` + série 2005–2025 |
| 5. Gráficos PNG (opcional) | `gerar_graficos_analise.py` | CSV etário | PNGs |

**Não versionar** `data_cache/` (~500 MB por ano). Já está no `.gitignore`.

---

## Pré-requisitos

- Python 3.9+
- Disco livre: ~2 GB se for baixar SIM 2022–2024
- Rede estável (downloads S3 ~470–530 MB/arquivo)

```bash
cd serie-demografica
pip install -r requirements.txt
```

Dependências mínimas dos scripts de extração: `pandas`, `requests`.

---

## 1. Download SIM + série etária + estimativa 2025

```bash
python brazil_deaths_by_age_2014_2025.py
```

### O que faz

1. Para cada ano de 2014 a 2024, tenta o CSV público:
   ```
   https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/DO{YY}OPEN.csv
   ```
   Exemplos: `DO22OPEN.csv`, `DO23OPEN.csv`, `DO24OPEN.csv`.
2. Salva em `data_cache/` (reutiliza cache se o arquivo já existir e for grande).
3. Conta óbitos por faixa etária a partir do campo `IDADE` (códigos 4xx/5xx = anos).
4. Consulta totais nacionais no Registro Civil:
   ```
   https://transparencia.registrocivil.org.br/api/record/death
     ?start_date={ano}-01-01&end_date={ano}-12-31
   ```
5. Calcula fator `SIM / RC` no ano `SIM_RC_CORRECTION_YEAR` (padrão **2023**).
6. Estima 2025: `RC_2025 × fator`, distribuído pela estrutura etária do SIM 2023.

### Saídas

| Arquivo | Conteúdo |
|---------|----------|
| `data_cache/DO##OPEN.csv` | Microdados brutos (local) |
| `brazil_deaths_by_age_2014_2025.csv` | Óbitos por faixa (anos com SIM + 2025) |
| `brazil_death_rates_by_age_2014_2025.csv` | Taxas por 100 mil + variação 14–25 |
| `proveniencia_2014_2025.json` | Fonte / evidência por ano |
| `brazil_deaths_by_age_2014_2025_meta.json` | Fator, totais RC, taxas |

### Disponibilidade S3

Em ago/2026, só **2022–2024** responderam HTTP 200 no padrão `DO##OPEN.csv`. Anos 2014–2021 podem retornar 403 — o script registra `ev-inference` / pulo e mantém taxas históricas via seed no código.

Para conferir um ano manualmente (PowerShell):

```powershell
Invoke-WebRequest -Method Head `
  "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/DO24OPEN.csv"
```

### IDADE no SIM (resumo)

| Prefixo | Significado neste pipeline |
|---------|----------------------------|
| `1xx`–`3xx` | minutos / horas / dias → &lt; 1 ano |
| `4xx`, `5xx` | idade em anos (`xx`) |
| `999` / inválido | ignorado |

Faixas de saída: `0-4`, `5-14`, `15-19`, `20-29`, `30-39`, `40-59`, `60-79`, `80+`.

---

## 2. Extração gripe e dengue (SIM)

**Requer** pelo menos um `DO*OPEN.csv` em `data_cache/` (rode o passo 1 antes).

```bash
python extract_gripe_dengue_sim.py
```

| CID-10 (CAUSABAS) | Contagem |
|-------------------|----------|
| `J09`, `J10*`, `J11*` | gripe / influenza |
| `A90*`, `A91*`, `A97*` | dengue |

**Saída:** `data/sim_gripe_dengue_por_ano.json`

A série longa de dengue SVS (2016–2025) usada no dashboard está em `data/obitos_gripe_dengue_2016_2025.json` (vigilância + SIM onde houver). Atualize o JSON do dashboard à mão ou reaproveite os totais SIM deste script.

Tempo típico: ~1 min por ano de microdado.

---

## 3. Extração câncer e miocardite (SIM)

```bash
python extract_cancer_miocardite_sim.py
```

| CID-10 (CAUSABAS) | Contagem |
|-------------------|----------|
| `C00`–`C97` | câncer (neoplasias malignas) |
| `I40*` | miocardite **aguda** (série principal) |
| `I41*`, `I514` | breakdown opcional no JSON SIM |

**Saídas:**

- `data/sim_cancer_miocardite_por_ano.json` — só anos com microdado  
- `data/obitos_cancer_miocardite_2014_2025.json` — série completa:
  - 2014–2021: seed (TabNet Cap. II × 0,98 / série I40 publicada)
  - anos com DO##: valores SIM
  - 2025: estimativa se existir `brazil_deaths_by_age_2014_2025_meta.json`

---

## 4. Extração suicídio (SIM)

```bash
python extract_suicidio_sim.py
```

| CID-10 (CAUSABAS) | Contagem |
|-------------------|----------|
| `X60`–`X84` | lesões autoprovocadas intencionalmente (série principal) |
| `Y870` | sequelas (breakdown opcional no JSON SIM) |

**Saídas:**

- `data/sim_suicidio_por_ano.json` — só anos com microdado  
- `data/obitos_suicidio_2005_2025.json` — série ~20 anos:
  - 2005–2021: seed TabNet / boletim MS (2021 = 15.507)
  - anos com DO##: valores SIM
  - 2025: estimativa se existir `brazil_deaths_by_age_2014_2025_meta.json`

O dashboard (`index.html`) embute a série no gráfico full-bleed e na coluna **Suicídio** da tabela 2016–2025. Inclui links de ajuda (CVV 188) e referências.

---

## 5. Gráficos PNG (opcional)

O dashboard (`index.html`) usa Chart.js e dados embutidos/JSON. Os PNGs são opcionais (README, OG image):

```bash
python gerar_graficos_analise.py
```

Requer `brazil_deaths_by_age_2014_2025.csv` e `brazil_death_rates_by_age_2014_2025.csv`.

---

## Ordem recomendada (do zero)

```bash
pip install -r requirements.txt

# 1) Baixa SIM (se necessário) + série etária + RC 2025
python brazil_deaths_by_age_2014_2025.py

# 2) Causas no cache
python extract_gripe_dengue_sim.py
python extract_cancer_miocardite_sim.py
python extract_suicidio_sim.py

# 3) Opcional
python gerar_graficos_analise.py

# 4) Abrir dashboard
start index.html   # Windows
# ou: open index.html / xdg-open index.html
```

---

## Atualizar o dashboard após nova extração

O `index.html` embute vários arrays em JavaScript. Depois de regenerar os JSON/CSV:

1. Abra `data/obitos_cancer_miocardite_2014_2025.json` e `data/obitos_gripe_dengue_2016_2025.json`
2. Atualize os blocos `DATA.cancerMio`, `DATA.disease`, `DATA.abs` / `DATA.rates` no `<script>` do `index.html` se os números mudarem
3. Ou mantenha o HTML alinhado aos JSON versionados no próximo commit

KPIs do topo do dashboard também são estáticos — revise ao mudar totais.

---

## Tags de evidência

| Tag | Significado |
|-----|-------------|
| `ev-confirmed` | Microdado SIM processado neste ambiente |
| `ev-surveillance` | Série oficial/publicada (SVS, TabNet, literatura) |
| `ev-inference` | Estimativa documentada (RC × fator, proporções) |
| `ev-gap` | Sem dado neste pipeline |

---

## Problemas comuns

| Sintoma | Causa provável | Ação |
|---------|----------------|------|
| `403` no S3 | Ano removido/renomeado no OpenDataSUS | Conferir portal; usar TabNet/FTP para anos antigos |
| Script de causa sem saída | `data_cache/` vazio | Rodar `brazil_deaths_by_age_2014_2025.py` antes |
| Stream CSV corta no meio | Timeout de rede | Usar cache local (o script grava arquivo completo) |
| Totais SIM ≠ SVS (dengue) | Critérios diferentes | Esperado — não misturar sem nota |
| I40 ≠ I40+I514 | Definição de miocardite | Dashboard usa **I40**; JSON SIM traz breakdown |

### Download manual (fallback)

1. Abra [OpenDataSUS — SIM](https://opendatasus.saude.gov.br/) ou o bucket S3 do CKAN Saúde  
2. Baixe `DO{YY}OPEN.csv` do ano desejado  
3. Coloque em `data_cache/` com o nome padrão (`DO24OPEN.csv`, etc.)  
4. Rode os extractors  

Portal RC: [transparencia.registrocivil.org.br](https://transparencia.registrocivil.org.br/registros)

---

## Script legado

`brazil_deaths_by_age_2015_2024.py` — pipeline antigo (faixas diferentes). Preferir `brazil_deaths_by_age_2014_2025.py`.

---

## Referências rápidas

- OpenDataSUS SIM: https://opendatasus.saude.gov.br/  
- TabNet Mortalidade: http://tabnet.datasus.gov.br/  
- Transparência Registro Civil: https://transparencia.registrocivil.org.br/  
- Artigos do projeto: pasta `artigos/`
