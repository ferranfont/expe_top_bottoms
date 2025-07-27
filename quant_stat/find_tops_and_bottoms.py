import pandas as pd

def extremes(df):
    """
    Detecta extremos alternos (top → bottom → top → ...) en el DataFrame.
    Usa columnas: 'high', 'low', 'atr_trigger_high', 'atr_trigger_low'.
    
    Devuelve: lista de tuplas (tipo, índice, valor)
    tipo ∈ {'top', 'bottom'}
    """

    extremos = []
    modo = 'top'  # empieza buscando top

    pending_max = df['high'].iloc[0]
    pending_max_i = 0

    pending_min = df['low'].iloc[0]
    pending_min_i = 0

    for i in range(1, len(df)):
        current_high = df['high'].iloc[i]
        current_low = df['low'].iloc[i]

        if modo == 'top':
            trigger = df['atr_trigger_high'].iloc[pending_max_i]
            if pd.isna(trigger):
                continue

            if current_high > pending_max:
                pending_max = current_high
                pending_max_i = i
            elif current_low < trigger:
                extremos.append(('top', pending_max_i, pending_max))
                modo = 'bottom'
                pending_min = current_low
                pending_min_i = i

        elif modo == 'bottom':
            trigger = df['atr_trigger_low'].iloc[pending_min_i]
            if pd.isna(trigger):
                continue

            if current_low < pending_min:
                pending_min = current_low
                pending_min_i = i
            elif current_high > trigger:
                extremos.append(('bottom', pending_min_i, pending_min))
                modo = 'top'
                pending_max = current_high
                pending_max_i = i

    return extremos
