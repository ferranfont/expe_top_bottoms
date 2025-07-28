import pandas as pd

def strat_guardian_clusters_OM(df, guardian_summary_df, keep_order=300, target_pts=2, stop_pts=2):
    """
    Simula la ejecución de órdenes buy limit desde guardian_summary_df y verifica:
    - Si se toca el precio de entrada.
    - Si se alcanza el take profit o stop loss.
    Calcula el beneficio en puntos y en USD (1 punto = 50 USD).

    Devuelve un DataFrame con tracking y estadísticas.
    """

    records = []

    for _, row in guardian_summary_df.iterrows():
        entry_index = row['min_index']
        entry_price = row['entry_price']
        tag = row['tag']

        tp_price = entry_price + target_pts
        sl_price = entry_price - stop_pts

        # Verifica si se toca el precio de entrada
        window = df.iloc[entry_index: entry_index + keep_order].copy()
        entry_hit = False
        entry_time = None
        outcome = 'timeout'
        exit_price = None
        exit_time = None
        profit_points = 0
        profit_usd = 0

        for i, (_, candle) in enumerate(window.iterrows()):
            if not entry_hit:
                if candle['low'] <= entry_price:
                    entry_hit = True
                    entry_time = candle['datetime']
            elif entry_hit:
                # Busca TP o SL después de entrada
                if candle['high'] >= tp_price:
                    outcome = 'target'
                    exit_price = tp_price
                    exit_time = candle['datetime']
                    profit_points = target_pts
                    profit_usd = profit_points * 50
                    break
                elif candle['low'] <= sl_price:
                    outcome = 'stop'
                    exit_price = sl_price
                    exit_time = candle['datetime']
                    profit_points = -stop_pts
                    profit_usd = profit_points * 50
                    break

        # Si no se salió pero se tocó entrada
        if entry_hit and outcome == 'timeout':
            last_candle = window.iloc[-1]
            exit_price = last_candle['close']
            exit_time = last_candle['datetime']
            profit_points = exit_price - entry_price
            profit_usd = profit_points * 50

        if entry_hit:
            records.append({
                'tag': tag,
                'entry_index': entry_index,
                'entry_time': entry_time,
                'entry_price': entry_price,
                'exit_time': exit_time,
                'exit_price': exit_price,
                'outcome': outcome,
                'profit_points': profit_points,
                'profit_usd': profit_usd
            })

    tracking_df = pd.DataFrame(records)

    # === Imprimir resumen
    print("\n📊 Tracking Record Summary:")
    print(tracking_df[['tag', 'entry_time', 'entry_price', 'exit_time', 'exit_price', 'outcome', 'profit_points', 'profit_usd']])

    total = len(tracking_df)
    wins = (tracking_df['outcome'] == 'target').sum()
    losses = (tracking_df['outcome'] == 'stop').sum()
    timeout = (tracking_df['outcome'] == 'timeout').sum()
    total_usd = tracking_df['profit_usd'].sum()

    print(f"\n✅ Total trades: {total}")
    print(f"🎯 Targets hit: {wins}")
    print(f"🛑 Stops hit: {losses}")
    print(f"⏰ Timeouts: {timeout}")
    print(f"💰 Total Profit: {total_usd:.2f} USD")

    return tracking_df

def strat_guardian_clusters_summary(guardian_df, shift_entry=2):
    summary_rows = []

    for tag, group in guardian_df.groupby('tag'):
        min_row = group[group['is_min']].iloc[0]
        summary_rows.append({
            'tag': tag,
            'min_value': min_row['min_value'],
            'min_index': min_row['index'],
            'entry_price': min_row['min_value'] - shift_entry
        })

    summary_df = pd.DataFrame(summary_rows)
    print("\n📌 RESUMEN GUARDIAN CLUSTERS:")
    print(summary_df)

    return summary_df
