# main.py
import pandas as pd
import os
import ta
from chart_volume import plot_close_and_volume
from datetime import time
#from quant_stat.find_tops_and_bottoms import find_tops
#from quant_stat.find_tops_and_bottoms import find_bottoms
from quant_stat.find_tops_and_bottoms import extremes


symbol = 'ES'
timeframe = 'tick_data'

# ====================================================
# 📥 CARGA DE DATOS
# ====================================================
directorio = '../DATA'
#nombre_fichero = 'ES_25_07_2025_30s_data.csv'
nombre_fichero ='ES_near_tick_data_27_jul_2025.csv'
ruta = os.path.join(directorio, nombre_fichero)

print("\n================================= 🔍 df  ===============================")
columnas = ['datetime', 'open', 'high', 'low', 'close', 'volume']
df = pd.read_csv(ruta, sep=';', names=columnas, header=None, decimal=',', encoding='utf-8')
df['datetime'] = pd.to_datetime(df['datetime'], format="%d/%m/%Y %H:%M", dayfirst=True)
df['date'] = df['datetime'].dt.date
df['time'] = df['datetime'].dt.time

df = df.set_index('datetime')



# Agrupar la data para tener menos filas
df = df.resample('1s').agg({
    'open': 'first',
    'high': 'max',
    'low': 'min',
    'close': 'last',
    'volume': 'sum'
}).dropna()



# ====================================================
# 📊 CÁLCULO DEL ATR DINÁMICO
# ====================================================
n= 14
df['atr'] = ta.volatility.AverageTrueRange(
    high=df['high'], low=df['low'], close=df['close'], window=n
).average_true_range()

df['atr_trigger_high'] = df['high']-df['atr']
df['atr_trigger_low'] = df['low']+df['atr']

# Mostrar resultado
print(df.tail())

# ====================================================
# 🔎 BUSCA TOPS AND BOTTOMS
# ====================================================
# asegúrate de que df['atr_trigger'] esté calculado previamente
extremos = extremes(df)
extremos_df = pd.DataFrame(extremos, columns=['type', 'index', 'value'])

print (extremos_df)

# Separar para graficar si lo necesitas
tops = [(i, val) for tipo, i, val in extremos if tipo == 'top']
bottoms = [(i, val) for tipo, i, val in extremos if tipo == 'bottom']




# ====================================================
# 📊 GENERACIÓN DEL GRÁFICO
# ====================================================

# df = df[df['date'].dt.time >= time(8, 0, 0)]              # subsegmento

df = df.reset_index()
df['date'] = pd.to_datetime(df['datetime'])  # si tu columna se llama así
df['time_str'] = df['date'].dt.strftime('%H:%M:%S')
unique_date = df['date'].dt.date.unique()[0] 
fecha = unique_date.strftime('%Y-%m-%d')

plot_close_and_volume(symbol, timeframe, df, fecha, tops=tops, bottoms=bottoms, extremos_df=extremos_df)



