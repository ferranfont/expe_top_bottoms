# main.py
import pandas as pd
import os
from chart_volume import plot_close_and_volume


symbol = 'ES'
timeframe = '1D'

# ====================================================
# 📥 CARGA DE DATOS
# ====================================================
directorio = '../DATA'
nombre_fichero = 'export_es_2015_formatted.csv'
ruta_completa = os.path.join(directorio, nombre_fichero)

print("\n======================== 🔍 df  ===========================")
df = pd.read_csv(ruta_completa)
print('Fichero:', ruta_completa, 'importado')
print(f"Características del Fichero Base: {df.shape}")

# Normalizar columnas a minúsculas y renombrar 'volumen' a 'volume'
df.columns = [col.strip().lower() for col in df.columns]
df = df.rename(columns={'volumen': 'volume'})

# Asegurar formato datetime con zona UTC
df['date'] = pd.to_datetime(df['date'], utc=True)
df = df.set_index('date')

# 🔁 Resample a velas diarias
df_daily = df.resample('1D').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()

# Reset index para usar 'date' como columna
df_daily = df_daily.reset_index()

print(df_daily.head())

# ====================================================
# 📊 GENERACIÓN DEL GRÁFICO
# ====================================================

plot_close_and_volume(symbol, timeframe, df_daily)
