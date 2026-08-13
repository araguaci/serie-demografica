# Changelog

Todas as mudanças relevantes deste projeto são documentadas neste arquivo.

O formato segue [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adota [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Unreleased]

### Planejado

- Breakdown de indeterminação Y10–Y34 por UF
- Atualização automática quando o OpenDataSUS republicar microdados

## [1.2.0] — 2026-08-13

### Added

- Série de suicídio CID-10 **X60–X84** (~20 anos, 2005–2025) no dashboard
- Contagem de **Y10–Y34** (intenção indeterminada) em `extract_suicidio_sim.py`
- Modelo de subnotificação **piso / central / teto** (`scripts/estimate_suicidio_subnotificacao.py`)
  - fator de realocação default **0,35** (faixa literatura 0,20–0,45)
- Dados versionados:
  - `data/sim_suicidio_por_ano.json`
  - `data/obitos_suicidio_2005_2025.json`
  - `data/obitos_suicidio_subnotificacao.json`
- Seção full-bleed no `index.html` com faixa piso–teto e barra central
- Coluna **Suicídio** na tabela 2016–2025 (valores centrais a partir de 2022)
- Tag de painel `ok-provisorio` para 2024 (lag de fechamento do SIM)
- Links de ajuda e campanhas: CVV 188, Setembro Amarelo, CAPS/UBS, SAMU 192
- Documentação metodológica:
  - `docs/NOTA-SUBNOTIFICACAO.md`
  - `docs/INVESTIGACAO-SUBNOTIFICACAO.md`
- Scripts exploratórios (pendentes de dados por UF):
  - `scripts/estimate_suicidio_subnotificacao_uf.py`
  - `scripts/correlate_subnotificacao_insolvencia.py`
- Arquivos `VERSION` e este `CHANGELOG.md`

### Changed

- README: estrutura, pipeline de suicídio/subnotificação, versão **1.2.0**
- `docs/EXTRACAO-DADOS.md`: etapa 4 (suicídio + Y10–Y34) e estimativa de subnotificação
- Rodapé e bloco “Método e proveniência” do dashboard alinhados ao modelo de três camadas
- Padrão Sentinel no README (Eixo SELVA)

### Fixed

- Interpretação da queda do piso X60–X84 em 2024 (14.095 vs 17.002 em 2023):
  **hipótese de lag confirmada** — taxa de indeterminação 2024 = **60,9%**
  (vs 48,6% em 2022 e 45,0% em 2023); estimativa central permanece ~21,8 mil

## [1.1.0] — 2026-08

### Added

- Dashboard premium (`index.html`) com Chart.js
- Série etária 2014–2025 (SIM + estimativa RC/ARPEN 2025)
- Óbitos por dengue (SVS) e gripe/influenza (SIM J09–J11)
- Óbitos por câncer (C00–C97) e miocardite aguda (I40)
- Extractors: `extract_gripe_dengue_sim.py`, `extract_cancer_miocardite_sim.py`
- Artigos X (`artigos/`) e guia `docs/EXTRACAO-DADOS.md`
- Compartilhamento social e créditos no rodapé

### Changed

- Pipeline canônico: `brazil_deaths_by_age_2014_2025.py`
- Proveniência explícita (`ev-confirmed` / `ev-surveillance` / `ev-inference` / `ev-gap`)

## [1.0.0] — 2026

### Added

- Análise inicial de mortalidade por faixa etária (Brasil)
- Scripts e painéis de referência (`Cursor.md`, gráficos PNG)

---

[Unreleased]: https://github.com/araguaci/serie-demografica/compare/v1.2.0...HEAD
[1.2.0]: https://github.com/araguaci/serie-demografica/compare/v1.1.0...v1.2.0
[1.1.0]: https://github.com/araguaci/serie-demografica/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/araguaci/serie-demografica/releases/tag/v1.0.0
