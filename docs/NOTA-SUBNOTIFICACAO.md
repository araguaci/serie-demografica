### Subnotificação — X60-X84 vs Y10-Y34 (proposta de nota para o painel)

**Problema:** óbitos por causas externas (suicídio, CID X60-X84) exigem
frequentemente perícia (IML) para definição da causa básica. Quando o
laudo é inconclusivo, ou o ano do SIM ainda não fechou completamente, o
óbito é classificado como **Y10-Y34 (intenção indeterminada)** em vez de
X60-X84. Isso gera três efeitos visíveis na série:

1. **Anos recentes parecem "cair"** (ex.: 2024 abaixo de 2023) — é lag de
   fechamento, não redução real.
2. **Heterogeneidade regional**: UFs com menor cobertura de perícia
   forense (tipicamente Norte/Nordeste) têm taxa de indeterminação maior.
3. **Viés sistemático de subestimação** do suicídio confirmado (X60-X84)
   como piso, não como valor real.

**Modelo de três camadas (piso / central / teto):**

| Camada | Definição | Evidência |
|---|---|---|
| Piso confirmado | X60-X84 puro | `ev-confirmed` |
| Central estimado | X60-X84 + (Y10-Y34 × fator) | `ev-inference` |
| Teto máximo | X60-X84 + Y10-Y34 (100% indeterminado = suicídio) | `ev-confirmed` como limite teórico, não como estimativa |

O `fator` de realocação (default 0,35, faixa 0,20–0,45 na literatura
epidemiológica brasileira) é o único parâmetro não observado — deve ficar
explícito no tooltip/rodapé do gráfico para não passar precisão falsa.

**Texto sugerido para o rodapé do gráfico de suicídio:**

> Óbitos confirmados (X60-X84) subestimam o total real de suicídios devido
> a eventos ainda classificados como intenção indeterminada (Y10-Y34) no
> momento da consulta. A faixa piso-teto no gráfico reflete essa incerteza;
> o valor central usa um fator de realocação de literatura (ev-inference),
> não um dado direto do SIM.

**Status no painel (2026-08-13):** implementado · release **v1.2.0**.

| Ano | Taxa Y10–Y34 / (X60+Y10) | Central (f=0,35) |
|-----|--------------------------|------------------|
| 2022 | 48,55% | 21.899 |
| 2023 | 44,97% | 21.866 |
| 2024 | **60,88%** (provisório) | 21.773 |

Hipótese de lag de fechamento **confirmada** nos microdados DO22–DO24.
Ver `data/obitos_suicidio_subnotificacao.json` e
`docs/INVESTIGACAO-SUBNOTIFICACAO.md`.

**Próximo passo natural:** comparar a taxa de indeterminação por UF, para
expor o viés regional como um mapa — insumo cruzado eventual com
insolvência/penduricalhos (hipótese a testar, não conclusão).
