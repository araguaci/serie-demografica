"""
Gera gráficos da análise demográfica (série 2014-2025).
Prioriza brazil_deaths_by_age_2014_2025.csv e brazil_death_rates_by_age_2014_2025.csv.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

plt.rcParams["font.family"] = "DejaVu Sans"
plt.rcParams["axes.unicode_minus"] = False

FAIXAS = ["0-4", "5-14", "15-19", "20-29", "30-39", "40-59", "60-79", "80+"]
CORES = ["#FF6B6B", "#4ECDC4", "#45B7D1", "#FFA07A", "#98D8C8", "#F7DC6F", "#BB8FCE", "#85C1E2"]

ABS_CSV = Path("brazil_deaths_by_age_2014_2025.csv")
RATES_CSV = Path("brazil_death_rates_by_age_2014_2025.csv")


def load_absolutos() -> pd.DataFrame:
    if not ABS_CSV.exists():
        raise FileNotFoundError(
            f"{ABS_CSV} não encontrado. Rode: python brazil_deaths_by_age_2014_2025.py"
        )
    df = pd.read_csv(ABS_CSV)
    return df.sort_values("Year")


def load_taxas() -> pd.DataFrame:
    if not RATES_CSV.exists():
        raise FileNotFoundError(f"{RATES_CSV} não encontrado.")
    df = pd.read_csv(RATES_CSV).set_index("Faixa Etária")
    df.columns = [int(c) if str(c).isdigit() else c for c in df.columns]
    return df


df_obitos = load_absolutos()
df_rates = load_taxas()

# Socioeconômico (contexto; não vem do pipeline SIM)
dados_socio = {
    "Ano": [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025],
    "Desemprego": [8.5, 12.0, 12.8, 12.3, 11.9, 13.5, 13.2, 9.3, 7.8, 6.5, 5.6],
    "PIB_per_Capita": [14800, 14200, 14500, 14900, 15100, 14200, 14800, 15500, 16200, 16800, 17200],
    "Expectativa_Vida": [75.2, 75.4, 75.6, 75.8, 76.0, 75.8, 72.8, 75.5, 76.4, 76.6, 76.8],
}
df_socio = pd.DataFrame(dados_socio)

fig = plt.figure(figsize=(20, 24))

# 1. Totais
ax1 = plt.subplot(4, 2, 1)
ax1.plot(df_obitos["Year"], df_obitos["Total_deaths"] / 1000, marker="o",
         linewidth=2.5, markersize=8, color="#2E86AB")
ax1.fill_between(df_obitos["Year"], df_obitos["Total_deaths"] / 1000, alpha=0.3, color="#2E86AB")
if 2025 in set(df_obitos["Year"]):
    ax1.axvline(2025, color="orange", linestyle="--", alpha=0.7, label="2025 estimado (RC)")
ax1.set_xlabel("Ano", fontsize=12, fontweight="bold")
ax1.set_ylabel("Óbitos Totais (milhares)", fontsize=12, fontweight="bold")
ax1.set_title("Evolução de Óbitos Totais (SIM 2022-2024 + RC 2025)", fontsize=14, fontweight="bold", pad=15)
ax1.grid(True, alpha=0.3, linestyle="--")
ax1.legend()
for ano, total in zip(df_obitos["Year"], df_obitos["Total_deaths"] / 1000):
    ax1.annotate(f"{total:.0f}K", (ano, total), textcoords="offset points",
                 xytext=(0, 10), ha="center", fontsize=9, fontweight="bold")

# 2. Stacked area
ax2 = plt.subplot(4, 2, 2)
ax2.stackplot(
    df_obitos["Year"],
    *[df_obitos[f] for f in FAIXAS],
    labels=FAIXAS, colors=CORES, alpha=0.7,
)
ax2.set_xlabel("Ano", fontsize=12, fontweight="bold")
ax2.set_ylabel("Número de Óbitos", fontsize=12, fontweight="bold")
ax2.set_title("Distribuição de Óbitos por Faixa Etária", fontsize=14, fontweight="bold", pad=15)
ax2.legend(loc="upper left", fontsize=8, ncol=4)
ax2.grid(True, alpha=0.3, linestyle="--")

# 3. Comparação primeiro vs último ano da série absoluta
ax3 = plt.subplot(4, 2, 3)
ano_a, ano_b = int(df_obitos["Year"].iloc[0]), int(df_obitos["Year"].iloc[-1])
x = np.arange(len(FAIXAS))
width = 0.35
dados_a = [df_obitos[df_obitos["Year"] == ano_a][f].values[0] for f in FAIXAS]
dados_b = [df_obitos[df_obitos["Year"] == ano_b][f].values[0] for f in FAIXAS]
ax3.bar(x - width / 2, dados_a, width, label=str(ano_a), color="#3498DB", alpha=0.8)
ax3.bar(x + width / 2, dados_b, width, label=str(ano_b), color="#E74C3C", alpha=0.8)
ax3.set_xlabel("Faixa Etária", fontsize=12, fontweight="bold")
ax3.set_ylabel("Número de Óbitos", fontsize=12, fontweight="bold")
ax3.set_title(f"Comparação de Óbitos: {ano_a} vs {ano_b}", fontsize=14, fontweight="bold", pad=15)
ax3.set_xticks(x)
ax3.set_xticklabels(FAIXAS, rotation=45, ha="right")
ax3.legend()
ax3.grid(True, alpha=0.3, axis="y", linestyle="--")

# 4. Taxas 2014-2025
ax4 = plt.subplot(4, 2, 4)
anos_taxa = sorted(c for c in df_rates.columns if isinstance(c, int))
for faixa in ["40-59", "60-79", "80+"]:
    ax4.plot(anos_taxa, [df_rates.loc[faixa, a] for a in anos_taxa],
             marker="o", label=faixa, linewidth=2, markersize=6)
ax4.set_xlabel("Ano", fontsize=12, fontweight="bold")
ax4.set_ylabel("Taxa por 100.000 habitantes", fontsize=12, fontweight="bold")
ax4.set_title("Taxas de Mortalidade (Adultos e Idosos) 2014-2025", fontsize=14, fontweight="bold", pad=15)
ax4.legend()
ax4.grid(True, alpha=0.3, linestyle="--")

# 5. Totais vs desemprego (anos em comum)
ax5 = plt.subplot(4, 2, 5)
merged = df_socio.merge(df_obitos[["Year", "Total_deaths"]], left_on="Ano", right_on="Year", how="inner")
if not merged.empty:
    ax5.scatter(merged["Desemprego"], merged["Total_deaths"] / 1000, s=150, alpha=0.6,
                color="#E74C3C", edgecolors="black", linewidth=2)
    for _, row in merged.iterrows():
        ax5.annotate(str(int(row["Ano"])), (row["Desemprego"], row["Total_deaths"] / 1000),
                     textcoords="offset points", xytext=(5, 5), fontsize=9, fontweight="bold")
ax5.set_xlabel("Taxa de Desemprego (%)", fontsize=12, fontweight="bold")
ax5.set_ylabel("Óbitos Totais (milhares)", fontsize=12, fontweight="bold")
ax5.set_title("Desemprego vs Óbitos Totais (anos com microdado/estimativa)", fontsize=14, fontweight="bold", pad=15)
ax5.grid(True, alpha=0.3, linestyle="--")

# 6. Indicadores normalizados
ax6 = plt.subplot(4, 2, 6)
base = df_socio[df_socio["Ano"] == 2015].iloc[0]
desemp_norm = 100 - ((df_socio["Desemprego"] - base["Desemprego"]) * 5)
pib_norm = (df_socio["PIB_per_Capita"] / base["PIB_per_Capita"]) * 100
exp_norm = (df_socio["Expectativa_Vida"] / base["Expectativa_Vida"]) * 100
ax6.plot(df_socio["Ano"], desemp_norm, marker="s", label="Desemprego (invertido)", linewidth=2, color="#E74C3C")
ax6.plot(df_socio["Ano"], pib_norm, marker="o", label="PIB per Capita", linewidth=2, color="#27AE60")
ax6.plot(df_socio["Ano"], exp_norm, marker="^", label="Expectativa de Vida", linewidth=2, color="#3498DB")
ax6.axhline(100, color="gray", linestyle="--", alpha=0.5, label="Base 2015")
ax6.set_xlabel("Ano", fontsize=12, fontweight="bold")
ax6.set_ylabel("Índice (2015 = 100)", fontsize=12, fontweight="bold")
ax6.set_title("Indicadores Socioeconômicos Normalizados", fontsize=14, fontweight="bold", pad=15)
ax6.legend()
ax6.grid(True, alpha=0.3, linestyle="--")

# 7. Heatmap composição etária (% do total)
ax7 = plt.subplot(4, 2, 7)
comp = df_obitos.set_index("Year")[FAIXAS]
comp_pct = comp.div(comp.sum(axis=1), axis=0) * 100
sns.heatmap(comp_pct.T, annot=True, fmt=".1f", cmap="YlOrRd", ax=ax7, cbar_kws={"shrink": 0.8})
ax7.set_title("Composição % dos Óbitos por Faixa e Ano", fontsize=14, fontweight="bold", pad=15)
ax7.set_xlabel("Ano")
ax7.set_ylabel("Faixa Etária")

# 8. Pizza último ano
ax8 = plt.subplot(4, 2, 8)
ultimo = int(df_obitos["Year"].iloc[-1])
vals = [df_obitos[df_obitos["Year"] == ultimo][f].values[0] for f in FAIXAS]
total = sum(vals)
pct = [(v / total) * 100 for v in vals]
wedges, texts, autotexts = ax8.pie(
    pct, labels=FAIXAS, autopct="%1.1f%%", colors=CORES, startangle=90, textprops={"fontsize": 9}
)
for t in autotexts:
    t.set_color("white")
    t.set_fontweight("bold")
sufixo = " estimado" if ultimo == 2025 else ""
ax8.set_title(f"Distribuição Percentual de Óbitos ({ultimo}{sufixo})", fontsize=14, fontweight="bold", pad=15)

plt.tight_layout(pad=3.0)
plt.savefig("analise_mortalidade_graficos_completos.png", dpi=300, bbox_inches="tight")
print("Gráficos salvos em: analise_mortalidade_graficos_completos.png")
plt.close()

# Série temporal detalhada
fig2, ax = plt.subplots(figsize=(16, 10))
for faixa, cor in zip(FAIXAS, CORES):
    ax.plot(df_obitos["Year"], df_obitos[faixa], marker="o", label=faixa,
            linewidth=2.5, markersize=6, color=cor)
if 2025 in set(df_obitos["Year"]):
    ax.axvline(2025, color="orange", linestyle="--", alpha=0.7, linewidth=2, label="2025 estimado (RC)")
ax.set_xlabel("Ano", fontsize=14, fontweight="bold")
ax.set_ylabel("Número de Óbitos", fontsize=14, fontweight="bold")
ax.set_title("Evolução de Óbitos por Faixa Etária (2022-2025)", fontsize=16, fontweight="bold", pad=20)
ax.legend(loc="upper left", fontsize=10, ncol=3)
ax.grid(True, alpha=0.3, linestyle="--")
plt.tight_layout()
plt.savefig("serie_temporal_faixas_etarias.png", dpi=300, bbox_inches="tight")
print("Gráfico de série temporal salvo em: serie_temporal_faixas_etarias.png")
plt.close()

print("\nTodos os graficos foram gerados com sucesso!")
