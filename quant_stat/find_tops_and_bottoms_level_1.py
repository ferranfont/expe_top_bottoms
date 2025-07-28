import pandas as pd

def extremes_level_1(df):
    """
    Detecta extremos alternos (top → bottom → top → ...) usando umbrales más exigentes.
    Usa: 'atr_trigger_high_x2' y 'atr_trigger_low_x2'
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
            trigger = df['atr_trigger_high_x2'].iloc[pending_max_i]
            if pd.isna(trigger):
                continue

            if current_high > pending_max:
                pending_max = current_high
                pending_max_i = i
            elif current_low < trigger:
                extremos.append(('top_1', pending_max_i, pending_max))
                modo = 'bottom'
                pending_min = current_low
                pending_min_i = i

        elif modo == 'bottom':
            trigger = df['atr_trigger_low_x2'].iloc[pending_min_i]
            if pd.isna(trigger):
                continue

            if current_low < pending_min:
                pending_min = current_low
                pending_min_i = i
            elif current_high > trigger:
                extremos.append(('bottom_1', pending_min_i, pending_min))
                modo = 'top'
                pending_max = current_high
                pending_max_i = i

    return extremos
