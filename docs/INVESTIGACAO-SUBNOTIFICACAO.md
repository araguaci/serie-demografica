# Investigação: gap de subnotificação na série de suicídio (X60–X84)

**Status:** teste 1 **confirmado** · ev-inference para camada central  
**Escopo:** `DATA.suicidio` (2005–2025), seção "Suicídio" do painel  
**Atualizado:** 2026-08-13 · **Release:** v1.2.0 ([CHANGELOG](../CHANGELOG.md))

---

## 1. Como o gap foi identificado

Ponto de partida: leitura direta do array já publicado no `index.html`
(objeto `DATA.suicidio`):

```js
years:  [...,2019,2020,2021, 2022,  2023,  2024,  2025],
piso:   [...,13523,13837,15507,16462,17002,14095, 15112],
```

O sinal de alerta é puramente aritmético: **2024 (14.095) é MENOR que
2023 (17.002) e menor até que 2022 (16.462)**, quebrando uma trajetória
de alta praticamente monotônica desde 2005.

**Pergunta:** essa queda é tendência real ou artefato de fechamento do SIM?

## 2. Hipótese mecanística

Óbitos por causas externas (CID X60–X84) frequentemente dependem de laudo
pericial (IML). Enquanto a investigação está aberta, o óbito costuma entrar
no SIM como **Y10–Y34** (intenção indeterminada).

**Implicação:** comparar 2024 "fechado hoje" com 2022/2023 já maduros é
comparar estágios de maturação diferentes.

## 3. Resultado do teste 1 (executado)

| Ano | X60–X84 (piso) | Y10–Y34 | Taxa indeterminação | Central (f=0,35) | Teto |
|-----|----------------|---------|---------------------|------------------|------|
| 2022 | 16.462 | 15.533 | **48,55%** | 21.899 | 31.995 |
| 2023 | 17.002 | 13.896 | **44,97%** | 21.866 | 30.898 |
| 2024 | 14.095 | 21.937 | **60,88%** | 21.773 | 36.032 |

**Hipótese confirmada:** `taxa_indeterminacao_2024 > 2022 e 2023`.

Com a estimativa central, a série 2022–2024 fica **estável (~21,8 mil)** —
a “queda” do piso some. O painel marca 2024 como `ok-provisorio` e exibe
faixa piso–teto.

Saída: `data/obitos_suicidio_subnotificacao.json`  
Script: `scripts/estimate_suicidio_subnotificacao.py`  
Extração: `extract_suicidio_sim.py` (agora conta Y10–Y34).

## 4. Classificação de evidência

- **ev-confirmed:** piso X60–X84 e contagens Y10–Y34 nos microdados DO22–DO24.
- **ev-inference:** central = X60–X84 + (Y10–Y34 × 0,35); interpretação de lag
  de fechamento em 2024; extrapolação 2025.
- **Não confundir** o `ok-provisorio` de 2024 (classificação pendente) com o
  `inf` de 2025 (extrapolação RC/ARPEN).

## 5. Ferramentas

1. **`extract_suicidio_sim.py`** — inclui `indeterminado_Y10_Y34` e
   `taxa_indeterminacao_pct`.
2. **`scripts/estimate_suicidio_subnotificacao.py`** — piso / central / teto
   (fator default 0,35, faixa 0,20–0,45).
3. **`estimate_suicidio_subnotificacao_uf.py`** — (pendente) viés regional.
4. **`correlate_subnotificacao_insolvencia.py`** — (pendente) exploratório.

## 6. Checklist

- [x] Contagem Y10–Y34 por ano no CSV/extração SIM
- [x] Rodar `estimate_suicidio_subnotificacao.py` e confirmar taxa 2024 maior
- [x] Atualizar tag 2024 para `ok-provisorio` no painel
- [x] Nota de rodapé do gráfico (`NOTA-SUBNOTIFICACAO.md`) no painel
- [x] Tabela 2016–2025 e Método/proveniência alinhados ao modelo
- [ ] (Opcional) Breakdown por UF
- [ ] (Opcional) Correlação com insolvência

## 7. Recursos de apoio

O painel mantém CVV (188), Setembro Amarelo, CAPS/UBS e SAMU (192).
Esta investigação é metodológica — os canais de apoio permanecem visíveis.
