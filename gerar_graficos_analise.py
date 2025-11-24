"""
Script para gerar gráficos da análise demográfica de mortalidade no Brasil (2015-2024)
Requisitos: pip install matplotlib pandas numpy seaborn
"""

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import seaborn as sns
from matplotlib import rcParams

# Configuração para português
plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['axes.unicode_minus'] = False

# Dados de óbitos por faixa etária (2015-2024)
dados_obitos = {
    'Ano': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    '0': [20800, 20400, 20100, 19800, 19500, 19200, 20200, 19500, 20200, 19800],
    '1-4': [4200, 4100, 4000, 3900, 3800, 3700, 3800, 3600, 3500, 3400],
    '5-14': [3800, 3700, 3600, 3500, 3400, 3300, 3400, 3200, 3100, 3000],
    '15-24': [28500, 29200, 29800, 30400, 30900, 31400, 32000, 30500, 29000, 28000],
    '25-44': [78200, 79500, 80800, 82100, 83300, 84500, 115000, 95000, 88000, 85000],
    '45-64': [142300, 145800, 149300, 152800, 156200, 159600, 209500, 180000, 165000, 160000],
    '65-74': [198500, 205200, 212000, 218800, 225500, 232200, 320000, 280000, 260000, 250000],
    '75-84': [285400, 295600, 305800, 316000, 326200, 336400, 450000, 400000, 380000, 370000],
    '85+': [437300, 466500, 494400, 523500, 551200, 580700, 645100, 488800, 452200, 435800],
    'Total': [1200000, 1250000, 1300000, 1350000, 1400000, 1450000, 1800000, 1500000, 1400000, 1350000]
}

# Dados socioeconômicos
dados_socio = {
    'Ano': [2015, 2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024],
    'Desemprego': [8.5, 12.0, 12.8, 12.3, 11.9, 13.5, 13.2, 9.3, 7.8, 6.5],
    'PIB_per_Capita': [14800, 14200, 14500, 14900, 15100, 14200, 14800, 15500, 16200, 16800],
    'Expectativa_Vida': [75.2, 75.4, 75.6, 75.8, 76.0, 75.8, 75.2, 75.5, 75.8, 76.0],
    'Gasto_Saude_PIB': [9.1, 9.3, 9.5, 9.7, 9.9, 10.2, 10.8, 10.5, 10.3, 10.1],
    'Anos_Escolaridade': [7.8, 7.9, 8.0, 8.1, 8.2, 8.2, 8.3, 8.4, 8.5, 8.6]
}

df_obitos = pd.DataFrame(dados_obitos)
df_socio = pd.DataFrame(dados_socio)

# Criar figura com múltiplos gráficos
fig = plt.figure(figsize=(20, 24))

# ========== GRÁFICO 1: Evolução de Óbitos Totais ==========
ax1 = plt.subplot(4, 2, 1)
ax1.plot(df_obitos['Ano'], df_obitos['Total']/1000, marker='o', linewidth=2.5, markersize=8, color='#2E86AB')
ax1.fill_between(df_obitos['Ano'], df_obitos['Total']/1000, alpha=0.3, color='#2E86AB')
ax1.set_xlabel('Ano', fontsize=12, fontweight='bold')
ax1.set_ylabel('Óbitos Totais (milhares)', fontsize=12, fontweight='bold')
ax1.set_title('Evolução de Óbitos Totais no Brasil (2015-2024)', fontsize=14, fontweight='bold', pad=15)
ax1.grid(True, alpha=0.3, linestyle='--')
ax1.axvline(x=2021, color='red', linestyle='--', alpha=0.5, label='Pico Pandemia')
ax1.legend()
for i, (ano, total) in enumerate(zip(df_obitos['Ano'], df_obitos['Total']/1000)):
    if ano in [2021, 2020, 2024]:
        ax1.annotate(f'{total:.1f}K', (ano, total), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontsize=9, fontweight='bold')

# ========== GRÁFICO 2: Distribuição por Faixa Etária (Stacked Area) ==========
ax2 = plt.subplot(4, 2, 2)
faixas = ['0', '1-4', '5-14', '15-24', '25-44', '45-64', '65-74', '75-84', '85+']
cores = ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FFA07A', '#98D8C8', '#F7DC6F', '#BB8FCE', '#85C1E2', '#F8B739']
ax2.stackplot(df_obitos['Ano'], 
              df_obitos['0'], df_obitos['1-4'], df_obitos['5-14'], df_obitos['15-24'],
              df_obitos['25-44'], df_obitos['45-64'], df_obitos['65-74'], df_obitos['75-84'], df_obitos['85+'],
              labels=faixas, colors=cores, alpha=0.7)
ax2.set_xlabel('Ano', fontsize=12, fontweight='bold')
ax2.set_ylabel('Número de Óbitos', fontsize=12, fontweight='bold')
ax2.set_title('Distribuição de Óbitos por Faixa Etária (Stacked Area)', fontsize=14, fontweight='bold', pad=15)
ax2.legend(loc='upper left', fontsize=8, ncol=3)
ax2.grid(True, alpha=0.3, linestyle='--')

# ========== GRÁFICO 3: Comparação 2015 vs 2024 (Barras) ==========
ax3 = plt.subplot(4, 2, 3)
anos_comparacao = [2015, 2024]
x = np.arange(len(faixas))
width = 0.35
dados_2015 = [df_obitos[df_obitos['Ano']==2015][f].values[0] for f in faixas]
dados_2024 = [df_obitos[df_obitos['Ano']==2024][f].values[0] for f in faixas]
ax3.bar(x - width/2, dados_2015, width, label='2015', color='#3498DB', alpha=0.8)
ax3.bar(x + width/2, dados_2024, width, label='2024', color='#E74C3C', alpha=0.8)
ax3.set_xlabel('Faixa Etária', fontsize=12, fontweight='bold')
ax3.set_ylabel('Número de Óbitos', fontsize=12, fontweight='bold')
ax3.set_title('Comparação de Óbitos por Faixa Etária: 2015 vs 2024', fontsize=14, fontweight='bold', pad=15)
ax3.set_xticks(x)
ax3.set_xticklabels(faixas, rotation=45, ha='right')
ax3.legend()
ax3.grid(True, alpha=0.3, axis='y', linestyle='--')

# ========== GRÁFICO 4: Taxa de Mortalidade por Faixa (Linhas) ==========
ax4 = plt.subplot(4, 2, 4)
# Calcular taxas (simplificado - usando população estimada)
populacao_estimada = {
    2015: 204000000, 2016: 206000000, 2017: 208000000, 2018: 210000000, 2019: 212000000,
    2020: 214000000, 2021: 216000000, 2022: 215000000, 2023: 216000000, 2024: 217000000
}
for i, faixa in enumerate(['25-44', '45-64', '65-74', '75-84', '85+']):
    taxas = []
    for ano in df_obitos['Ano']:
        obitos = df_obitos[df_obitos['Ano']==ano][faixa].values[0]
        pop = populacao_estimada[ano]
        # Estimativa grosseira de população por faixa (ajustar conforme necessário)
        taxa = (obitos / pop) * 100000
        taxas.append(taxa)
    ax4.plot(df_obitos['Ano'], taxas, marker='o', label=faixa, linewidth=2, markersize=6)
ax4.set_xlabel('Ano', fontsize=12, fontweight='bold')
ax4.set_ylabel('Taxa por 100.000 habitantes', fontsize=12, fontweight='bold')
ax4.set_title('Taxa de Mortalidade por Faixa Etária (Adultos e Idosos)', fontsize=14, fontweight='bold', pad=15)
ax4.legend()
ax4.grid(True, alpha=0.3, linestyle='--')

# ========== GRÁFICO 5: Correlação Desemprego vs Mortalidade ==========
ax5 = plt.subplot(4, 2, 5)
mortalidade_25_64 = []
for ano in df_socio['Ano']:
    obitos_25_44 = df_obitos[df_obitos['Ano']==ano]['25-44'].values[0]
    obitos_45_64 = df_obitos[df_obitos['Ano']==ano]['45-64'].values[0]
    mortalidade_25_64.append(obitos_25_44 + obitos_45_64)
ax5.scatter(df_socio['Desemprego'], mortalidade_25_64, s=150, alpha=0.6, color='#E74C3C', edgecolors='black', linewidth=2)
# Adicionar linha de tendência
z = np.polyfit(df_socio['Desemprego'], mortalidade_25_64, 1)
p = np.poly1d(z)
ax5.plot(df_socio['Desemprego'], p(df_socio['Desemprego']), "r--", alpha=0.8, linewidth=2, label='Tendência')
# Anotar anos
for i, ano in enumerate(df_socio['Ano']):
    if ano in [2015, 2021, 2024]:
        ax5.annotate(str(ano), (df_socio['Desemprego'].iloc[i], mortalidade_25_64[i]),
                    textcoords="offset points", xytext=(5,5), ha='left', fontsize=9, fontweight='bold')
ax5.set_xlabel('Taxa de Desemprego (%)', fontsize=12, fontweight='bold')
ax5.set_ylabel('Óbitos Faixas 25-64 anos', fontsize=12, fontweight='bold')
ax5.set_title('Correlação: Desemprego vs Mortalidade (Faixas Economicamente Ativas)', 
              fontsize=14, fontweight='bold', pad=15)
ax5.legend()
ax5.grid(True, alpha=0.3, linestyle='--')

# ========== GRÁFICO 6: Indicadores Socioeconômicos Normalizados ==========
ax6 = plt.subplot(4, 2, 6)
# Normalizar para índice base 2015 = 100
base_2015 = df_socio[df_socio['Ano']==2015]
desemprego_norm = 100 - ((df_socio['Desemprego'] - base_2015['Desemprego'].values[0]) * 5)  # Invertido
pib_norm = (df_socio['PIB_per_Capita'] / base_2015['PIB_per_Capita'].values[0]) * 100
expectativa_norm = (df_socio['Expectativa_Vida'] / base_2015['Expectativa_Vida'].values[0]) * 100
ax6.plot(df_socio['Ano'], desemprego_norm, marker='s', label='Desemprego (invertido)', linewidth=2, color='#E74C3C')
ax6.plot(df_socio['Ano'], pib_norm, marker='o', label='PIB per Capita', linewidth=2, color='#27AE60')
ax6.plot(df_socio['Ano'], expectativa_norm, marker='^', label='Expectativa de Vida', linewidth=2, color='#3498DB')
ax6.axhline(y=100, color='gray', linestyle='--', alpha=0.5, label='Base 2015')
ax6.set_xlabel('Ano', fontsize=12, fontweight='bold')
ax6.set_ylabel('Índice (2015 = 100)', fontsize=12, fontweight='bold')
ax6.set_title('Evolução de Indicadores Socioeconômicos Normalizados', fontsize=14, fontweight='bold', pad=15)
ax6.legend()
ax6.grid(True, alpha=0.3, linestyle='--')

# ========== GRÁFICO 7: Heatmap de Correlação ==========
ax7 = plt.subplot(4, 2, 7)
# Preparar dados para correlação
dados_corr = pd.DataFrame({
    'Mortalidade_Total': df_obitos['Total'],
    'Mortalidade_25_64': [df_obitos[df_obitos['Ano']==a]['25-44'].values[0] + 
                          df_obitos[df_obitos['Ano']==a]['45-64'].values[0] for a in df_socio['Ano']],
    'Mortalidade_65+': [df_obitos[df_obitos['Ano']==a]['65-74'].values[0] + 
                        df_obitos[df_obitos['Ano']==a]['75-84'].values[0] + 
                        df_obitos[df_obitos['Ano']==a]['85+'].values[0] for a in df_socio['Ano']],
    'Desemprego': df_socio['Desemprego'],
    'PIB_per_Capita': df_socio['PIB_per_Capita'],
    'Expectativa_Vida': df_socio['Expectativa_Vida'],
    'Gasto_Saude': df_socio['Gasto_Saude_PIB'],
    'Escolaridade': df_socio['Anos_Escolaridade']
})
corr_matrix = dados_corr.corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='coolwarm', center=0, 
            square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax7)
ax7.set_title('Matriz de Correlação: Mortalidade vs Indicadores Socioeconômicos', 
              fontsize=14, fontweight='bold', pad=15)

# ========== GRÁFICO 8: Distribuição Percentual 2024 ==========
ax8 = plt.subplot(4, 2, 8)
dados_2024_pct = [df_obitos[df_obitos['Ano']==2024][f].values[0] for f in faixas]
total_2024 = df_obitos[df_obitos['Ano']==2024]['Total'].values[0]
percentuais = [(d/total_2024)*100 for d in dados_2024_pct]
# Gráfico de pizza
wedges, texts, autotexts = ax8.pie(percentuais, labels=faixas, autopct='%1.1f%%', 
                                    colors=cores, startangle=90, textprops={'fontsize': 9})
for autotext in autotexts:
    autotext.set_color('white')
    autotext.set_fontweight('bold')
ax8.set_title('Distribuição Percentual de Óbitos por Faixa Etária (2024)', 
              fontsize=14, fontweight='bold', pad=15)

plt.tight_layout(pad=3.0)
plt.savefig('analise_mortalidade_graficos_completos.png', dpi=300, bbox_inches='tight')
print("Gráficos salvos em: analise_mortalidade_graficos_completos.png")
plt.close()

# ========== GRÁFICO ADICIONAL: Série Temporal Detalhada por Faixa ==========
fig2, ax = plt.subplots(figsize=(16, 10))
for faixa, cor in zip(faixas, cores):
    ax.plot(df_obitos['Ano'], df_obitos[faixa], marker='o', label=faixa, 
            linewidth=2.5, markersize=6, color=cor)
ax.set_xlabel('Ano', fontsize=14, fontweight='bold')
ax.set_ylabel('Número de Óbitos', fontsize=14, fontweight='bold')
ax.set_title('Evolução de Óbitos por Faixa Etária (2015-2024)', fontsize=16, fontweight='bold', pad=20)
ax.legend(loc='upper left', fontsize=10, ncol=3)
ax.grid(True, alpha=0.3, linestyle='--')
ax.axvline(x=2021, color='red', linestyle='--', alpha=0.5, linewidth=2, label='Pico Pandemia')
plt.tight_layout()
plt.savefig('serie_temporal_faixas_etarias.png', dpi=300, bbox_inches='tight')
print("Gráfico de série temporal salvo em: serie_temporal_faixas_etarias.png")
plt.close()

print("\nTodos os graficos foram gerados com sucesso!")
print("Arquivos criados:")
print("   - analise_mortalidade_graficos_completos.png (8 graficos)")
print("   - serie_temporal_faixas_etarias.png (serie temporal detalhada)")

