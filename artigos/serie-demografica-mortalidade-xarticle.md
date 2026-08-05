# Brasil: quem morre, e de quê

Em 2024 o SIM registrou **1.426.346** óbitos no Brasil. Em 2025, com o microdado oficial ainda fechado, o Registro Civil aponta para algo perto de **1,53 milhão** depois da correção SIM/RC.

O número bruto importa menos do que a composição. Quase sete em cada dez mortes caem nas faixas **60–79** e **80+**. Em paralelo, a dengue fez em 2024 o que a série da vigilância não via há décadas: **6.264** óbitos confirmados.

Montei um observatório aberto — série etária 2014–2025, gripe e dengue na última década — com proveniência marcada em cada ano. Sem tratar estimativa como fato fechado.

## O que mudou na mortalidade por idade

Entre 2014 e 2025, as taxas por 100 mil mostram um padrão claro:

- **5–14 anos:** −16,2%
- **0–4 anos:** −10,6%
- **20–29 anos:** −6,4%
- **60–79 anos:** +6,7%
- **80+ anos:** +6,2%

Crianças e jovens caem. Idosos sobem. Não é mistério: a pirâmide envelhece e a carga de mortes acompanha.

O pico da pandemia ainda aparece nas taxas de 2021. Depois disso, 2022–2024 recuam. O total SIM de 2024 (1,426 mi) é o menor da janela recente pós-COVID — e mesmo assim a estrutura etária continua concentrada no topo.

## Como estimar 2025 sem mentir no rótulo

O OpenDataSUS entregou DO22, DO23 e DO24. O SIM 2025 ainda não saiu (nem preliminar, nesta data).

Para não truncar a série, usei o Portal da Transparência do Registro Civil (ARPEN):

- RC 2023: **1.448.725**
- SIM 2023: **1.465.610**
- Fator SIM/RC: **1,011655**
- RC 2025: **1.511.682**
- Estimativa corrigida: **1.529.301**

A distribuição etária de 2025 replica a estrutura do SIM 2023. Tag de evidência: **ev-inference**. Quando o SIM preliminar sair, esse número deve ser revisado — não defendido.

> “Dado oficial até 2024; 2025 estimado via Registro Civil corrigido. Nenhum óbito de 2025 entra como fechado antes da hora.”

## Dengue: o ano que quebrou a série

Óbitos confirmados pela vigilância (SVS/MS), 2016–2025:

| Ano | Óbitos |
|-----|--------|
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

\*Painel MS com confirmações parciais; ainda havia óbitos em investigação.

2024 não é “mais um ano ruim”. É ruptura. No SIM, causa básica A90/A91/A97 deu **6.620** óbitos em 2024 — ordem de grandeza alinhada à vigilância, com critério diferente.

## Gripe: o retorno depois do silêncio pandêmico

Influenza no SIM (causa básica J09–J11), onde o microdado existe:

- **2022:** 3.249
- **2023:** 1.334
- **2024:** 2.269

2016–2021 ficam em aberto neste pipeline: o S3 do OpenDataSUS não serviu esses anos agora, e inventar série “bonita” seria fraude metodológica. Para referência paralela, o SRAG 2019 contou **1.176** óbitos hospitalares classificados como influenza — outra métrica, outro universo.

O ponto é simples: gripe voltou a matar em volume visível depois de 2020–2021. Dengue, em 2024, matou em outra escala.

## Por que separar SIM, RC e SVS

Três fontes, três jobs:

1. **SIM** — causa básica e idade no atestado (padrão ouro demográfico)
2. **Registro Civil** — contagem quase em tempo real, sem detalhe etário completo
3. **SVS/SINAN** — óbitos confirmados de dengue na vigilância

Misturar as três sem etiqueta produz gráfico bonito e conclusão errada. Por isso cada linha do dataset carrega fonte e evidência (`ev-confirmed` / `ev-inference` / `ev-gap`).

## O que o dashboard mostra

O projeto [série-demográfica](https://serie-demografica.vercel.app/) reúne:

- KPIs de totais 2024/2025 e picos de dengue/gripe
- Taxas etárias 2019–2025 (variação 14–25 na tabela)
- Óbitos absolutos por faixa (SIM + estimativas documentadas)
- Série dengue SVS 2016–2025 e gripe SIM 2022–2024
- Código e CSVs no GitHub, microdados brutos fora do repo (~1,5 GB locais)

Não é painel de marketing. É observatório com costura à mostra.

## O que ainda falta

Gripe SIM 2016–2021 via TabNet/FTP. Fechamento limpo da dengue 2025 quando as investigações caírem. Substituição da estimativa RC assim que o SIM 2025 aparecer.

Até lá, o aviso permanece no rodapé: **2025 não é oficial**.

## Fontes

- DATASUS / OpenDataSUS — microdados SIM (DO22OPEN, DO23OPEN, DO24OPEN)
- Portal da Transparência do Registro Civil (ARPEN-Brasil) — totais de óbitos
- Ministério da Saúde / SVS — óbitos confirmados de dengue
- IBGE — contexto demográfico e tábuas de mortalidade

*Dossiê e código: [serie-demografica.vercel.app](https://serie-demografica.vercel.app/) · [github.com/araguaci/serie-demografica](https://github.com/araguaci/serie-demografica)*
