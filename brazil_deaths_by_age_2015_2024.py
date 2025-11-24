"""
Extrai e monta: brazil_deaths_by_age_2015_2024.csv
Requisitos: pandas, requests
Rodar: pip install pandas requests openpyxl
"""

import os
import io
import requests
import pandas as pd
from zipfile import ZipFile

# ---------- CONFIGURAÇÃO (edite se necessário) ----------
# Lista de URLs OpenDataSUS (exemplo a partir dos recursos identifyados)
# Ajuste/adicione os anos que desejar; aqui 2015..2024 (para 2024 pode ser preliminar)
s3_base = "https://s3.sa-east-1.amazonaws.com/ckan.saude.gov.br/SIM/"
# Nomes observados no OpenDataSUS (ver páginas): DO15OPEN.csv ... DO23OPEN.csv, DO24OPEN.csv (se existir)
years = list(range(2015, 2025))
csv_filenames = [f"DO{y % 100:02d}OPEN.csv" for y in years]  # ex: DO15OPEN.csv, DO24OPEN.csv
csv_urls = [s3_base + name for name in csv_filenames]

# Faixas alvo (padronizadas)
target_age_bins = [
    ("0", ["0"]), 
    ("1-4", ["1-4","01-04","1 a 4"]), 
    ("5-14", ["5-14","05-14","5 a 14"]),
    ("15-24", ["15-24","15 a 24"]),
    ("25-44", ["25-44","25 a 44"]),
    ("45-64", ["45-64","45 a 64"]),
    ("65-74", ["65-74","65 a 74"]),
    ("75-84", ["75-84","75 a 84"]),
    ("85+", ["85+","85 e mais","85 a 99","90+","90 a 99"])
]

# Coluna de saída por faixa
age_cols = [b[0] for b in target_age_bins]

# ---------- FUNÇÕES ----------
def download_csv(url):
    print("Baixando:", url)
    r = requests.get(url, timeout=60)
    r.raise_for_status()
    return r.content

def sniff_and_load_csv(content_bytes):
    # tenta ler direto como CSV com pandas
    try:
        return pd.read_csv(io.BytesIO(content_bytes), encoding='utf-8', low_memory=False)
    except Exception:
        # fallback: latin1
        return pd.read_csv(io.BytesIO(content_bytes), encoding='latin1', low_memory=False)

def normalize_age_label(age_label):
    if pd.isna(age_label):
        return ""
    s = str(age_label).strip().lower()
    # padronizações simples
    s = s.replace("anos","").replace(" a ","-").replace(" e mais","+").replace("ou mais","+").strip()
    return s

# ---------- PROCESSAMENTO ----------
rows_by_year = {}
for url, y in zip(csv_urls, years):
    try:
        content = download_csv(url)
        df = sniff_and_load_csv(content)
    except Exception as e:
        print(f"Não foi possível baixar/ler {url}: {e}")
        continue

    # Inspecionar colunas: procurar colunas que contenham 'idade' e 'ano' e 'obito' / 'num'
    cols = [c.lower() for c in df.columns]
    # heurística para localizar colunas
    col_age = next((c for c in df.columns if 'idade' in c.lower() or 'faixa' in c.lower()), None)
    col_year = next((c for c in df.columns if 'ano' in c.lower() or 'ano_do_obito' in c.lower()), None)
    col_count = next((c for c in df.columns if 'obito' in c.lower() or 'quantidade' in c.lower() or 'valor'==c.lower()), None)
    if col_age is None:
        # fallback: tentar colunas padrão
        if 'IDADE' in df.columns:
            col_age = 'IDADE'
        else:
            print("Coluna de idade não encontrada; amostra de colunas:", df.columns[:10])
            col_age = df.columns[0]  # força, mas avisa
    if col_count is None:
        # procurar colunas numéricas plausíveis
        numeric_cols = [c for c in df.columns if pd.api.types.is_numeric_dtype(df[c])]
        if numeric_cols:
            col_count = numeric_cols[-1]
        else:
            col_count = df.columns[-1]

    # Normalizar e agrupar por faixa
    df['age_raw'] = df[col_age].astype(str).apply(lambda x: x.strip())
    df['age_norm'] = df['age_raw'].apply(normalize_age_label)
    # agregar óbitos por faixa raw
    agg = df.groupby('age_norm')[col_count].sum().reset_index().rename(columns={'age_norm':'age','{}'.format(col_count):'deaths'})
    # criar dicionário por target bins
    out = { 'Year': y }
    total = 0
    for target, synonyms in target_age_bins:
        matched = agg[agg['age'].isin([s.lower() for s in synonyms])]
        # se não houver correspondência direta, tentar correspondência parcial
        if matched.empty:
            matched = agg[agg['age'].str.contains(target.replace('+','').split('-')[0], na=False)]
        val = int(matched['deaths'].sum()) if not matched.empty else 0
        out[target] = val
        total += val
    out['Total_deaths'] = int(agg['deaths'].sum())
    rows_by_year[y] = out

# montar DataFrame final
df_out = pd.DataFrame.from_dict(rows_by_year, orient='index').sort_index()
# preencher 0s e salvar
df_out = df_out.fillna(0).astype(int)
df_out.to_csv("brazil_deaths_by_age_2015_2024.csv", index=False)
print("Arquivo gerado: brazil_deaths_by_age_2015_2024.csv")
# ---------- FIM ----------
