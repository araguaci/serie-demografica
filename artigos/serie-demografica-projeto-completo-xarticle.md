# Observatório de mortalidade no Brasil (2014–2025)

Quem morre, em que idade, e de quê.

Este projeto reúne a série demográfica de óbitos por faixa etária com quatro causas que importam para o debate público: **dengue**, **gripe**, **câncer** e **miocardite aguda**. Tudo com fonte, critério CID e etiqueta de evidência. Estimativa não se disfarça de dado fechado.

Dashboard: [serie-demografica.vercel.app](https://serie-demografica.vercel.app/)  
Código: [github.com/araguaci/serie-demografica](https://github.com/araguaci/serie-demografica)

## Totais: o chão da série

Óbitos no Brasil (SIM / RC):

| Ano | Total | Fonte |
|-----|------:|-------|
| 2022 | 1.544.266 | SIM OpenDataSUS |
| 2023 | 1.465.610 | SIM OpenDataSUS |
| 2024 | 1.426.346 | SIM OpenDataSUS |
| 2025* | 1.529.301 | RC/ARPEN × fator SIM/RC |

\*SIM 2025 ainda não publicado. Registro Civil 2025 = 1.511.682; fator calculado em 2023 (SIM 1.465.610 / RC 1.448.725 = **1,011655**). Tag: **ev-inference**.

2024 é o menor total recente pós-pico pandêmico. A estrutura etária, porém, não “rejuvenesceu”: a carga segue nos idosos.

## Idade: crianças caem, 60+ sobe

Variação das taxas por 100 mil, **2014 → 2025**:

- **5–14 anos:** −16,2%
- **0–4 anos:** −10,6%
- **20–29 anos:** −6,4%
- **30–39 anos:** −3,0%
- **40–59 anos:** +5,8%
- **60–79 anos:** +6,7%
- **80+ anos:** +6,2%

O dashboard mostra taxas e óbitos absolutos na janela **2019–2025** (2019–2021 absolutos estimados via razões de taxa quando o S3 não tinha DO##OPEN). A tabela de variação mantém o pivô em 2014.

Quase sete em cada dez mortes caem em **60–79** e **80+**. Qualquer leitura de causa precisa desse chão demográfico.

## Dengue: a ruptura de 2024

Óbitos confirmados SVS/MS (vigilância), 2016–2025:

| Ano | Óbitos |
|----:|-------:|
| 2016 | 701 |
| 2017 | 185 |
| 2018 | 201 |
| 2019 | 840 |
| 2020 | 574 |
| 2021 | 246 |
| 2022 | 1.016 |
| 2023 | 1.179 |
| **2024** | **6.264** |
| 2025 | ~1.008* |

\*Painel MS com confirmações parciais e óbitos em investigação.

No SIM (causa básica A90/A91/A97): **1.279** (2022), **1.322** (2023), **6.620** (2024). Vigilância e SIM não são a mesma métrica — e mesmo assim 2024 é ruptura nas duas.

## Gripe: volta depois do silêncio

Influenza no SIM (J09–J11), onde o microdado existe:

- **2022:** 3.249  
- **2023:** 1.334  
- **2024:** 2.269  

2016–2021 ficam em aberto neste pipeline (CSV antigo indisponível no S3). Não invento série. Referência paralela: SRAG 2019 com **1.176** óbitos hospitalares classificados como influenza — outro universo.

## Câncer: a linha que quase não desce

Neoplasias malignas **C00–C97**:

| Ano | Óbitos | Evidência |
|----:|-------:|-----------|
| 2014 | ~197.9 mil | Cap. II × 0,98 |
| 2019 | ~230.6 mil | Cap. II × 0,98 |
| 2020 | ~224.7 mil | queda pandêmica |
| 2022 | **238.623** | SIM |
| 2023 | **249.942** | SIM — pico recente |
| 2024 | **238.511** | SIM |
| 2025* | ~255.7 mil | estimativa |

Monteiro et al. (2025) somaram **2.276.158** óbitos por neoplasias (Cap. II) em 2014–2023; 2023 foi o ano mais alto (**255.037** no Cap. II). Malignas ≈ 98% desse total — base do fator usado nos anos sem microdado.

## Miocardite aguda: raro, e em alta

CID **I40** apenas (não mistura com I51.4):

| Ano | Óbitos |
|----:|-------:|
| 2014 | 119 |
| 2019 | **100** (mínimo) |
| 2021 | 158 |
| 2022 | 163 |
| 2023 | 161 |
| **2024** | **201** |
| 2025* | ~215 |

2014–2023: série DATASUS publicada. 2022–2024: conferem com a contagem SIM nos DO##OPEN. Do fundo de 2019 ao SIM 2024, quase dobra.

No dashboard, câncer e miocardite aparecem **lado a lado**, cada um com escala própria. Comparar altura visual entre os dois painéis é erro.

## Por que três fontes (e etiquetas)

| Fonte | Serve para |
|-------|------------|
| **SIM** | Causa básica e idade no atestado |
| **RC/ARPEN** | Total quase em tempo real (2025) |
| **SVS/SINAN** | Dengue confirmada na vigilância |

Tags usadas no projeto:

- **ev-confirmed** — microdado SIM processado  
- **ev-surveillance** — série oficial/publicada sem CSV local  
- **ev-inference** — estimativa documentada (RC, proporções)  
- **ev-gap** — sem dado neste pipeline  

Misturar sem etiqueta produz gráfico bonito e conclusão errada.

## O que o repositório entrega

- Dashboard premium (Chart.js): KPIs, idade, dengue/gripe, câncer/miocardite  
- `brazil_deaths_by_age_2014_2025.py` — série etária SIM + RC 2025  
- `extract_gripe_dengue_sim.py` — J09–J11 e A90/A91/A97  
- `extract_cancer_miocardite_sim.py` — C00–C97 e I40  
- JSONs/CSVs agregados em `data/`  
- Microdados brutos (~1,5 GB) **fora do git** (`data_cache/`)

## O que ainda falta

SIM 2025 oficial. Gripe 2016–2021 via TabNet/FTP. Fechamento limpo da dengue 2025. Revisão das estimativas de 2025 (totais, câncer, miocardite) quando o microdado sair.

Até lá, o rodapé vale: **2025 não é oficial**.

## Fontes

- DATASUS / OpenDataSUS — SIM DO22OPEN, DO23OPEN, DO24OPEN  
- Portal da Transparência do Registro Civil (ARPEN-Brasil)  
- Ministério da Saúde / SVS — óbitos confirmados de dengue  
- Monteiro et al., *Mortality due to neoplasms in Brazil from 2014 to 2023*, MOJ Public Health (2025)  
- Série miocardite aguda 2014–2023 — DATASUS (publicação Revista FT, 2025)  
- IBGE — contexto demográfico  

*Projeto completo: [serie-demografica.vercel.app](https://serie-demografica.vercel.app/) · [github.com/araguaci/serie-demografica](https://github.com/araguaci/serie-demografica)*
