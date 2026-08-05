# Câncer sobe, miocardite dobra, dengue explode

Três curvas, um país.

Entre 2014 e 2024 o Brasil ganhou dezenas de milhares de mortes por câncer. No mesmo intervalo, a miocardite aguda (CID I40) saiu de **119** óbitos para **201**. E a dengue, em um único ano, **2024**, confirmou **6.264** mortes na vigilância — ruptura de escala.

Atualizei o observatório [série-demográfica](https://serie-demografica.vercel.app/) com essas séries lado a lado, cada ponto com fonte e tag de evidência. Sem maquiar buraco de dado.

## Câncer: a linha que quase não desce

Óbitos por neoplasias malignas (C00–C97), série 2014–2025:

| Ano | Óbitos | Nota |
|-----|--------|------|
| 2014 | ~197.9 mil | Cap. II TabNet × 0,98 |
| 2019 | ~230.6 mil | Cap. II × 0,98 |
| 2020 | ~224.7 mil | queda na pandemia |
| 2022 | **238.623** | SIM confirmado |
| 2023 | **249.942** | SIM — pico recente |
| 2024 | **238.511** | SIM |
| 2025* | ~255.7 mil | estimativa |

\*2025 = participação do câncer no total de 2024 × total RC corrigido (~1,53 mi). Tag: **ev-inference**.

A tendência de fundo é envelhecimento + carga crônica. 2020 quebra a subida. 2023 estoura. 2024 recua sem voltar ao patamar de 2014 — nem perto.

Monteiro et al. (2025), com TabNet/SIM Cap. II (neoplasias), somaram **2.276.158** óbitos em 2014–2023; 2023 foi o ano mais alto da década (**255.037** neoplasias no Cap. II). Malignas respondem por ~98% desse universo — daí o fator 0,98 nos anos sem microdado S3.

## Miocardite aguda: número pequeno, curva feia

CID **I40** apenas (miocardite aguda). Não misturo com I51.4.

| Ano | Óbitos I40 |
|-----|------------|
| 2014 | 119 |
| 2015 | 130 |
| 2016 | 127 |
| 2017 | 127 |
| 2018 | 118 |
| **2019** | **100** |
| 2020 | 120 |
| 2021 | 158 |
| 2022 | 163 |
| 2023 | 161 |
| **2024** | **201** |
| 2025* | ~215 |

2014–2023 vêm da série DATASUS publicada (Revista FT). 2022 e 2023 batem com a contagem SIM que rodei nos microdados OpenDataSUS (**163** e **161**). 2024, no SIM: **201**.

O mínimo da década é 2019. Depois disso a curva sobe e não volta. Em volume absoluto isso ainda é “raro” perto do câncer. Em variação percentual, é outra conversa: do fundo de 2019 ao SIM 2024, quase dobra.

> Escalas dos gráficos no dashboard são independentes. Comparar altura visual entre câncer e miocardite é erro de leitura.

## Dengue 2024 ainda é o choque da década

Só para não perder o fio: vigilância SVS fechou 2024 com **6.264** óbitos confirmados. No SIM (A90/A91/A97): **6.620**. 2025 segue com ~1.008 confirmados no painel e investigações abertas.

Gripe (J09–J11) no SIM: 3.249 (2022), 1.334 (2023), 2.269 (2024). Voltou depois do silêncio pandêmico — em outra ordem de grandeza que a dengue daquele ano.

## Idade: quem carrega o total

Taxas por 100 mil, variação 2014→2025:

- **5–14:** −16,2%
- **0–4:** −10,6%
- **60–79:** +6,7%
- **80+:** +6,2%

Totais SIM: 2022 = 1.544.266 · 2023 = 1.465.610 · 2024 = 1.426.346.  
2025 estimado via RC/ARPEN × fator SIM/RC 2023 (**1,011655**) → **1.529.301** (**ev-inference**).

Quase 70% das mortes seguem em 60+. Câncer cresce nesse chão demográfico. Dengue e miocardite são picos de causa — um epidêmico, outro raro e em alta.

## Método sem truque

1. **SIM** — causa básica no atestado (padrão ouro)
2. **TabNet / literatura** — preenche anos sem CSV no S3, com etiqueta
3. **RC/ARPEN** — só para total 2025, corrigido, nunca vendido como oficial
4. **SVS** — dengue confirmada na vigilância (critério ≠ SIM)

Cada série no JSON traz `ev-confirmed`, `ev-surveillance` ou `ev-inference`. Buraco de gripe 2016–2021 continua buraco: não invento.

## Onde ver

Dashboard: gráficos de câncer e miocardite **lado a lado** (2014–2025), mais idade, dengue e gripe.

[serie-demografica.vercel.app](https://serie-demografica.vercel.app/)

Código e agregados: [github.com/araguaci/serie-demografica](https://github.com/araguaci/serie-demografica)  
Microdados brutos (~1,5 GB) ficam fora do git, no cache local.

## O que falta

SIM 2025 oficial. Gripe 2016–2021 via TabNet/FTP. Fechamento da dengue 2025. Revisão das estimativas de câncer/miocardite 2025 quando o microdado sair.

Até lá: **2025 não é oficial**.

## Fontes

- DATASUS / OpenDataSUS — SIM DO22–DO24 (C00–C97, I40, J09–J11, A90–A91–A97)
- Monteiro et al., “Mortality due to neoplasms in Brazil from 2014 to 2023”, MOJ Public Health (2025) — TabNet Cap. II
- Série miocardite aguda 2014–2023 — DATASUS / Revista FT (2025)
- Ministério da Saúde / SVS — óbitos confirmados de dengue
- Portal da Transparência do Registro Civil (ARPEN) — totais 2023 e 2025

*Dossiê: [serie-demografica.vercel.app](https://serie-demografica.vercel.app/) · [github.com/araguaci/serie-demografica](https://github.com/araguaci/serie-demografica)*
