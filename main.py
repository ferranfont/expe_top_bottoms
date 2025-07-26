# main.py
import pandas as pd
import os
from chart_volume import plot_close_and_volume
from datetime import time


symbol = 'ES'
timeframe = '1D'

# ====================================================
# 📥 CARGA DE DATOS
# ====================================================
directorio = '../DATA'
#nombre_fichero = 'ES_25_07_2025_30s_data.csv'
nombre_fichero ='export.csv'
ruta = os.path.join(directorio, nombre_fichero)

print("\n================================= 🔍 df  ===============================")
columnas = ['datetime', 'open', 'high', 'low', 'close', 'volume']
df = pd.read_csv(ruta, sep=';', names=columnas, header=None, decimal=',', encoding='utf-8')
df['datetime'] = pd.to_datetime(df['datetime'], format="%d/%m/%Y %H:%M", dayfirst=True)
df['date'] = df['datetime'].dt.date
df['time'] = df['datetime'].dt.time

df = df.set_index('datetime')

# Mostrar resultado
print(df.head())

df = df.resample('5s').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()

# ====================================================
# 📊 GENERACIÓN DEL GRÁFICO
# ====================================================

# 1. Asegura que el índice se convierta en columna (si es datetime index)
df = df.reset_index()

# 2. Asegura que 'datetime' esté en formato datetime completo
df['date'] = pd.to_datetime(df['datetime'])  # si tu columna se llama así

# 3. Extrae la hora como string (solo para casos que uses time_str)
df['time_str'] = df['date'].dt.strftime('%H:%M:%S')

# 4. Ordena por fecha
df = df.sort_values('date')
df = df[df['date'].dt.time >= time(8, 0, 0)]

# 5. Extrae la fecha única y formatea para usar en el título
unique_date = df['date'].dt.date.unique()[0]
fecha = unique_date.strftime('%Y-%m-%d')

# 6. Llamada al gráfico
plot_close_and_volume(symbol, timeframe, df, fecha)

