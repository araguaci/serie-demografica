# 📊 Série Demográfica — Mortalidade por Faixa Etária no Brasil

## 🛡️ Sentinel Status
- **Status:** 🟢 Produção
- **Tier:** A
- **Health:** 85%
- **Stack:** Python, HTML/Chart.js, JSON versionado (`data/`), Vercel
- **ROI Potencial:** Impacto editorial / SELVA — série demográfica com fonte auditável (SIM/DATASUS + Registro Civil)

---

Observatório demográfico com série histórica de óbitos por faixa etária no Brasil (2014–2025) e causas selecionadas (gripe, dengue, câncer, miocardite, suicídio). SIM/DATASUS oficial até 2024; 2025 estimado via Registro Civil (ARPEN) com fator SIM/RC e etiqueta de evidência — hipótese ≠ fato. Suicídio usa modelo piso/central/teto (X60–X84 + Y10–Y34).

**Site:** [serie-demografica.vercel.app](https://serie-demografica.vercel.app) · **Repo:** [github.com/araguaci/serie-demografica](https://github.com/araguaci/serie-demografica)

**Eixo SELVA:** mesma disciplina dos hubs investigativos — [Sabor Brazil](https://sabor-brazil.vercel.app), [Vítimas do Estado](https://vitimas-do-estado.vercel.app), [Geoengenharia](https://geoengenharia.vercel.app), [República Sequestrada](https://republica-sequestrada-hub.vercel.app), [Lawfare Timeline](https://lawfare-timeline.vercel.app) — fonte primária, proveniência e deploy rastreável. Estratégia estável no monorepo: `docs/estrategia/SENTINEL-EIXO-SELVA.md`.

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/)
[![Version](https://img.shields.io/badge/Version-1.2.0-teal.svg)](CHANGELOG.md)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-Produção-success.svg)]()

---

## 📋 Índice

- [Sobre o Projeto](#sobre-o-projeto)
- [Características](#características)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Instalação](#instalação)
- [Uso](#uso)
- [Download e extração](#download-e-extração)
- [Fontes de Dados](#fontes-de-dados)
- [Principais Achados](#principais-achados)
- [Gráficos e Visualizações](#gráficos-e-visualizações)
- [Documentação](#documentação)
- [Versionamento](#versionamento)
- [Contribuindo](#contribuindo)
- [Licença](#licença)

---

## 🎯 Sobre o Projeto

Este projeto realiza uma análise demográfica abrangente da mortalidade no Brasil, segmentada por faixas etárias, cobrindo o período de 2014 a 2025. A análise integra dados de múltiplas fontes oficiais e correlaciona padrões de mortalidade com indicadores socioeconômicos, incluindo:

- **Economia**: PIB per capita, inflação, renda média
- **Emprego**: Taxa de desemprego, taxa de emprego
- **Saúde**: Gasto em saúde, expectativa de vida, mortalidade infantil
- **Educação**: Anos médios de escolaridade, taxa de alfabetização
- **Previdência**: Beneficiários INSS, expectativa de vida aos 60 anos

### Objetivos

1. Identificar tendências de mortalidade por faixa etária nos últimos 10 anos
2. Correlacionar padrões de mortalidade com indicadores socioeconômicos
3. Analisar o impacto de eventos críticos (crise econômica 2015-2016, pandemia COVID-19)
4. Fornecer insights para políticas públicas em saúde, educação e previdência
5. Comparar o Brasil com países de IDH similar

---

## ✨ Características

- ✅ **Análise Multissetorial**: Integra dados de economia, emprego, saúde, educação e previdência
- ✅ **Série Histórica Completa**: 2014-2025 (pivô 2014; 2025 com proveniência ev-inference)
- ✅ **Suicídio (X60–X84)**: série ~20 anos (2005–2025) + coluna na tabela 2016–2025 + links de ajuda (CVV 188)
- ✅ **Subnotificação**: modelo piso / central / teto com Y10–Y34 (fator 0,35); 2024 marcado como provisório
- ✅ **Visualizações Interativas**: Gráficos e tabelas comparativas
- ✅ **Fontes Confiáveis**: Dados oficiais de IBGE, DATASUS, World Bank, UNDP
- ✅ **Scripts Automatizados**: Extração e processamento de dados
- ✅ **Documentação Completa**: `docs/`, `CHANGELOG.md`, análises em Markdown e HTML

---

## 📁 Estrutura do Projeto

```
serie-demografica/
│
├── README.md / VERSION / CHANGELOG.md
├── index.html                            # Dashboard (Chart.js)
├── data/                                 # JSON agregados versionados
├── data_cache/                           # Microdados SIM (gitignored)
│
├── brazil_deaths_by_age_2014_2025.py     # Download SIM + RC + série etária
├── extract_gripe_dengue_sim.py           # J09–J11 / A90–A97
├── extract_cancer_miocardite_sim.py      # C00–C97 / I40
├── extract_suicidio_sim.py               # X60–X84 + Y10–Y34
├── gerar_graficos_analise.py             # PNGs opcionais
│
├── scripts/
│   ├── estimate_suicidio_subnotificacao.py      # piso / central / teto
│   ├── estimate_suicidio_subnotificacao_uf.py   # exploratório por UF
│   └── correlate_subnotificacao_insolvencia.py  # exploratório
│
├── docs/
│   ├── README.md
│   ├── EXTRACAO-DADOS.md
│   ├── NOTA-SUBNOTIFICACAO.md
│   └── INVESTIGACAO-SUBNOTIFICACAO.md
│
└── artigos/                              # X Articles + hero images
```

---

## 🚀 Instalação

### Pré-requisitos

- Python 3.9 ou superior
- pip (gerenciador de pacotes Python)

### Passo a Passo

1. **Clone o repositório** (ou baixe os arquivos):
```bash
git clone <url-do-repositorio>
cd serie-demografica
```

2. **Instale as dependências**:
```bash
pip install pandas numpy matplotlib seaborn requests openpyxl
```

Ou usando requirements.txt (criar se necessário):
```bash
pip install -r requirements.txt
```

---

## 💻 Uso

Fluxo rápido (do zero):

```bash
pip install -r requirements.txt
python brazil_deaths_by_age_2014_2025.py      # baixa SIM + RC, gera série etária
python extract_gripe_dengue_sim.py            # gripe + dengue no cache
python extract_cancer_miocardite_sim.py       # câncer + miocardite no cache
python extract_suicidio_sim.py                # suicídio X60–X84 + Y10–Y34
python scripts/estimate_suicidio_subnotificacao.py  # piso / central / teto
python gerar_graficos_analise.py              # PNGs opcionais
```

Abra `index.html` no navegador (idade, dengue/gripe, câncer/miocardite, suicídio).

---

## 📥 Download e extração

Instruções completas (URLs S3, API ARPEN, CIDs, cache, tags de evidência, troubleshooting):

**→ [docs/EXTRACAO-DADOS.md](docs/EXTRACAO-DADOS.md)**

Resumo:

| Script | Função |
|--------|--------|
| `brazil_deaths_by_age_2014_2025.py` | Download `DO##OPEN.csv` → `data_cache/`; faixas etárias; fator SIM/RC; estimativa 2025 |
| `extract_gripe_dengue_sim.py` | Conta J09–J11 e A90/A91/A97 no cache |
| `extract_cancer_miocardite_sim.py` | Conta C00–C97 e I40; atualiza série 2014–2025 |
| `extract_suicidio_sim.py` | Conta X60–X84 e Y10–Y34; série 2005–2025 |
| `scripts/estimate_suicidio_subnotificacao.py` | Modelo piso / central / teto (fator 0,35) |
| `gerar_graficos_analise.py` | PNGs a partir dos CSV etários |

`data_cache/` não vai para o git (~1,5 GB). Agregados versionados ficam em `data/` e nos CSV da raiz.

---

## 📊 Fontes de Dados

### Fontes Primárias

| Fonte | Dados Fornecidos | Período | Qualidade |
|-------|------------------|---------|-----------|
| **DATASUS/SIM** | Óbitos por faixa etária, causas, localização | 2014-2024 | Oficial até 2024 (OpenDataSUS) |
| **RC/ARPEN** | Óbitos totais (tempo quase real) | 2025 | Estimativa corrigida (ev-inference) |
| **IBGE** | Tábuas completas de mortalidade, população | 2015-2024 | Final até 2022, estimativas 2023-2024 |
| **Ministério da Saúde** | Mortalidade infantil, causas evitáveis | 2015-2024 | Final até 2023 |
| **World Bank (WDI)** | PIB per capita, gasto em saúde, educação | 2015-2024 | Anual |
| **ILOSTAT** | Taxa de desemprego, emprego por idade | 2015-2024 | Trimestral/Anual |
| **UNDP** | IDH, expectativa de vida, anos de escolaridade | 2015-2024 | Anual |
| **INSS** | Dados previdenciários, beneficiários por idade | 2015-2024 | Mensal/Anual |

### Links Úteis

- [DATASUS TabNet](http://tabnet.datasus.gov.br)
- [IBGE - Tábuas de Mortalidade](https://www.ibge.gov.br/estatisticas/sociais/populacao/9126-tabuas-completas-de-mortalidade.html)
- [OpenDataSUS](https://opendatasus.saude.gov.br)
- [World Bank Data](https://data.worldbank.org)
- [UNDP Human Development Reports](https://hdr.undp.org)

---

## 🔍 Principais Achados

### Mortalidade Infantil
- ✅ **Redução de 62%** na mortalidade infantil por causas evitáveis desde 1996
- 📉 Taxa de 14,5 para 14,0 por mil nascidos vivos (2015-2024)

### Impacto da Pandemia COVID-19
- ⚠️ **Pico em 2021**: 1,8 milhão de óbitos (+24% vs 2019)
- 👴 **68,2% dos óbitos** em pessoas com 60+ anos
- 📈 Faixa 25-44 anos: aumento de 38% (83.300 → 115.000 óbitos)
- 📈 Faixa 45-64 anos: aumento de 34% (156.200 → 209.500 óbitos)

### Envelhecimento Populacional
- 📊 Concentração crescente de óbitos em idosos (65+)
- 📈 Faixa 85+: crescimento de 14,5% em números absolutos (2015-2024)
- 💰 Pressão sobre sistema previdenciário

### Correlações Identificadas
- 🔗 **Desemprego vs Mortalidade (25-64 anos)**: Correlação +0.85
- 🔗 **Educação vs Mortalidade**: Correlação -0.82
- 🔗 **Expectativa de Vida vs Mortalidade**: Correlação -0.91

### Mortes Violentas
- ✅ **Queda histórica em 2024**: 44.127 casos (menor desde 2011)
- 📉 Redução de 5% vs 2023

---

## 📈 Gráficos e Visualizações

### Gráficos Disponíveis

1. **Evolução de Óbitos Totais (2015-2024)**
   - Mostra tendência geral e impacto da pandemia

2. **Distribuição por Faixa Etária (Stacked Area)**
   - Visualização da composição etária dos óbitos ao longo do tempo

3. **Comparação 2015 vs 2024**
   - Análise comparativa entre início e fim do período

4. **Taxa de Mortalidade por Faixa**
   - Taxas padronizadas por 100.000 habitantes

5. **Correlação Desemprego vs Mortalidade**
   - Análise de correlação para faixas economicamente ativas

6. **Indicadores Socioeconômicos Normalizados**
   - Comparação de múltiplos indicadores em escala normalizada

7. **Matriz de Correlação**
   - Heatmap de correlações entre variáveis

8. **Distribuição Percentual 2024**
   - Gráfico de pizza com distribuição atual

### Como Visualizar

Os gráficos são gerados automaticamente ao executar `gerar_graficos_analise.py`. Abra os arquivos PNG gerados em qualquer visualizador de imagens.

---

## 📝 Padronização de Faixas Etárias

Para análise comparativa, utilizamos as seguintes faixas padronizadas:

- **0**: Menores de 1 ano
- **1-4**: 1 a 4 anos completos
- **5-14**: 5 a 14 anos completos
- **15-24**: 15 a 24 anos completos
- **25-44**: 25 a 44 anos completos
- **45-64**: 45 a 64 anos completos
- **65-74**: 65 a 74 anos completos
- **75-84**: 75 a 84 anos completos
- **85+**: 85 anos e mais

---

## 🤝 Contribuindo

Contribuições são bem-vindas! Para contribuir:

1. **Fork** o projeto
2. Crie uma **branch** para sua feature (`git checkout -b feature/AmazingFeature`)
3. **Commit** suas mudanças (`git commit -m 'Add some AmazingFeature'`)
4. **Push** para a branch (`git push origin feature/AmazingFeature`)
5. Abra um **Pull Request**

### Áreas de Contribuição

- 📊 Atualização de dados com anos mais recentes
- 🐛 Correção de bugs nos scripts
- 📈 Novos tipos de visualizações
- 📝 Melhorias na documentação
- 🔍 Análises adicionais ou correlações

---

## ⚠️ Limitações e Notas Metodológicas

### Limitações dos Dados

1. **Dados Preliminares 2024**: Alguns indicadores de 2024 são estimativas/preliminares
2. **Sub-registro**: Possível sub-registro de óbitos em áreas remotas (Norte/Nordeste)
3. **Causas de Morte**: Classificação pode variar entre anos (mudanças em CID)
4. **População Base**: Estimativas populacionais podem ter margem de erro

### Notas Metodológicas

1. **Padronização de Faixas**: Diferentes fontes usam faixas diferentes; padronizamos para análise comparativa
2. **Correlações**: Correlação não implica causalidade; análises multivariadas seriam necessárias para causalidade
3. **Defasagem Temporal**: Alguns efeitos (ex: educação) têm impacto com defasagem de anos
4. **Fatores Não Observados**: Variáveis não incluídas podem influenciar resultados

---

## 📚 Referências e Bibliografia

### Documentos Oficiais

- IBGE - Tábuas Completas de Mortalidade (2022)
- UNDP - Relatório de Desenvolvimento Humano (2024)
- OMS - Global Health Estimates (2024)
- World Bank - World Development Indicators (2024)

### Artigos e Estudos

- Análises demográficas do IBGE
- Relatórios do Ministério da Saúde
- Estudos do IPEA sobre violência
- Publicações da OPAS sobre saúde nas Américas

---

## 📄 Licença

Este projeto está sob a licença MIT. Veja o arquivo `LICENSE` para mais detalhes.

**Nota**: Os dados utilizados são de domínio público e pertencem às respectivas instituições oficiais (IBGE, DATASUS, etc.). Este projeto é apenas uma análise e visualização desses dados.

---

## 👤 Autor

**Análise Demográfica Profissional**

- Análise baseada em dados oficiais
- Fontes confiáveis e verificáveis
- Metodologia transparente

---

## 🙏 Agradecimentos

- **IBGE** - Instituto Brasileiro de Geografia e Estatística
- **DATASUS** - Departamento de Informática do SUS
- **Ministério da Saúde** - Dados de mortalidade
- **World Bank** - Indicadores econômicos globais
- **UNDP** - Dados de desenvolvimento humano
- **OMS/OPAS** - Dados de saúde global

---

## 📞 Contato e Suporte

Para questões, sugestões ou problemas:

- Abra uma **Issue** no repositório
- Consulte a documentação em `Cursor.md`
- Verifique os scripts Python para detalhes técnicos

---

## 📚 Documentação

| Recurso | Descrição |
|---------|-----------|
| [docs/README.md](docs/README.md) | Índice da documentação |
| [docs/EXTRACAO-DADOS.md](docs/EXTRACAO-DADOS.md) | Pipeline operacional completo |
| [docs/NOTA-SUBNOTIFICACAO.md](docs/NOTA-SUBNOTIFICACAO.md) | Modelo piso / central / teto |
| [docs/INVESTIGACAO-SUBNOTIFICACAO.md](docs/INVESTIGACAO-SUBNOTIFICACAO.md) | Gap 2024 — lag de fechamento confirmado |
| [CHANGELOG.md](CHANGELOG.md) | Histórico de versões |

Em crise emocional: **CVV 188** · [cvv.org.br](https://www.cvv.org.br) · SAMU **192**

---

## 🏷️ Versionamento

Este repositório usa [SemVer](https://semver.org/lang/pt-BR/) (`MAJOR.MINOR.PATCH`).

| Arquivo | Papel |
|---------|-------|
| [`VERSION`](VERSION) | Versão canônica atual (`1.2.0`) |
| [`CHANGELOG.md`](CHANGELOG.md) | Notas por release (Keep a Changelog) |

Tags Git sugeridas: `v1.2.0`, `v1.1.0`, …

### Versão atual

- **Versão**: **1.2.0** (2026-08-13)
- **Período coberto**: mortalidade etária 2014–2025 · suicídio 2005–2025
- **Destaque 1.2.0**: suicídio + subnotificação Y10–Y34 (central ~21,8 mil em 2022–2024)

### Planejado

- [ ] Breakdown de indeterminação por UF
- [ ] Atualização automática quando o OpenDataSUS republicar microdados
- [ ] Análise por região/estado no dashboard
- [ ] API para acesso aos dados processados

---

<div align="center">

**⭐ Se este projeto foi útil, considere dar uma estrela! ⭐**

Made with ❤️ for demographic research

</div>

