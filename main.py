# main.py
import pandas as pd
import os
import ta
from chart_volume import plot_close_and_volume
from chart_volume_level import plot_close_and_volume_levels
from datetime import time
#from quant_stat.find_tops_and_bottoms import find_tops
#from quant_stat.find_tops_and_bottoms import find_bottoms
from quant_stat.find_tops_and_bottoms import extremes
from quant_stat.find_tops_and_bottoms_level_1 import extremes_level_1
from quant_stat.find_guardian_bottoms import group_consecutive_bottoms
from strat_OM.strat_OM_buy_fake_BO import strat_guardian_clusters_OM
from strat_OM.strat_OM_buy_fake_BO import strat_guardian_clusters_summary 

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

# Triggers para nivel 0 (más amplios)
df['atr_trigger_high'] = df['high']-df['atr']
df['atr_trigger_low'] = df['low']+df['atr']


# Triggers para nivel 1 (más amplios)
df['atr_trigger_high_x2'] = df['high'] - 3 * df['atr']
df['atr_trigger_low_x2'] = df['low'] + 3 * df['atr']

# Mostrar resultado
print(df.tail())

# ====================================================
# 🔎 BUSCA TOPS AND BOTTOMS NIVEL 0
# ====================================================
# asegúrate de que df['atr_trigger'] esté calculado previamente
extremos = extremes(df)
extremos_df = pd.DataFrame(extremos, columns=['type', 'index', 'value'])
# Separar para graficar si lo necesitas
tops = [(i, val) for tipo, i, val in extremos if tipo == 'top_0']
bottoms = [(i, val) for tipo, i, val in extremos if tipo == 'bottom_0']

# ====================================================
# 🔎 BUSCA TOPS AND BOTTOMS NIVEL 1
# ====================================================

extremos_lvl1 = extremes_level_1(df)
extremos_df_lvl1 = pd.DataFrame(extremos_lvl1, columns=['type', 'index', 'value'])
tops_1 = [(i, val) for tipo, i, val in extremos_lvl1 if tipo == 'top_1']
bottoms_1 = [(i, val) for tipo, i, val in extremos_lvl1 if tipo == 'bottom_1']
print ('Bottoms_nivel 1', '\n',extremos_df_lvl1)

# ====================================================
# 🔎 BUSQUEDA DE  SUELOS CONSECUTIVOS
# ====================================================
guardian_df = group_consecutive_bottoms(bottoms, guardian=2, max_gap=4)
print(guardian_df)
# Resetear antes de usar índices numéricos
df = df.reset_index()
df['date'] = pd.to_datetime(df['datetime'])  # asegúrate de que existe esta columna

# === Generar líneas horizontales para guardian ===
guardian_lines = []

for cluster_id in guardian_df['cluster_id'].unique():
    group = guardian_df[guardian_df['cluster_id'] == cluster_id]
    start_idx = group['index'].min()
    end_idx = group['index'].max()
    y_value = group['min_value'].iloc[0]
    tag = group['tag'].iloc[0]

    # CORREGIDO: usar iloc directamente porque df está ordenado y con índice numérico
    start_time = df.iloc[start_idx]['date']
    end_time = df.iloc[end_idx]['date']

    guardian_lines.append({
        'x0': start_time,
        'x1': end_time,
        'y': y_value,
        'tag': tag
    })

# ====================================================
# 📊 STRATEGY
# ====================================================


guardian_summary = strat_guardian_clusters_summary(guardian_df, shift_entry=0.75)
# Ejecuta estrategia completa
tracking_record_buy_fake_bo = strat_guardian_clusters_OM(
    df=df,
    guardian_summary_df=guardian_summary,
    keep_order=300,
    target_pts=10,
    stop_pts=5
)

# ====================================================
# 📊 GENERACIÓN DEL GRÁFICO
# ====================================================

# df = df[df['date'].dt.time >= time(8, 0, 0)]              # subsegmento

df = df.reset_index()
df['date'] = pd.to_datetime(df['datetime'])  # si tu columna se llama así
df['time_str'] = df['date'].dt.strftime('%H:%M:%S')
unique_date = df['date'].dt.date.unique()[0] 
fecha = unique_date.strftime('%Y-%m-%d')

plot_close_and_volume(symbol, timeframe, df, fecha, tops=tops, bottoms=bottoms, extremos_df=extremos_df, extremos_df_lvl1=extremos_df_lvl1)

# ====================================================
# 📊 GENERACIÓN DEL GRÁFICO LEVELS - SOLO ESTRUCTURA
# ====================================================

# Llamada al gráfico completo con niveles 0 y 1
plot_close_and_volume_levels(
    symbol=symbol,
    timeframe=timeframe,
    df=df,
    date_str=fecha,
    tops=tops,
    bottoms=bottoms,
    extremos_df=extremos_df,
    extremos_df_lvl1=extremos_df_lvl1,
    guardian_lines=guardian_lines,
    guardian_summary=guardian_summary,
    tracking_record_buy_fake_bo=tracking_record_buy_fake_bo
)


