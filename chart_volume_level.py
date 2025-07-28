import os
import pandas as pd
import webbrowser
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_close_and_volume_levels(symbol, timeframe, df, date_str,
                          tops=None, bottoms=None,
                          extremos_df=None, extremos_df_lvl1=None, guardian_lines=None, guardian_summary=None,tracking_record_buy_fake_bo=None):
    
    html_path = f'charts/close_vol_chart_{symbol}_{timeframe}_{date_str}_levels.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    # Crear figura con 2 subplots: precios y volumen
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.02
    )

    # === Velas con transparencia ===
    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='rgba(0,255,0,0.04)',
        decreasing_line_color='rgba(255,0,0,0.04)',
        increasing_fillcolor='rgba(0,255,0,0.04)',
        decreasing_fillcolor='rgba(255,0,0,0.04)',
        name='Velas'
    ), row=1, col=1)

    fecha_linea = pd.to_datetime(f"{date_str} 15:30:00")
    fig.add_shape(
        type="line",
        x0=fecha_linea,
        y0=0,
        x1=fecha_linea,
        y1=1,
        xref='x',
        yref='paper',
        line=dict(color="grey", width=1, dash="solid"),
        name="Apertura NY"
    )

    # === Volumen ===
    fig.add_trace(go.Bar(
        x=df['date'], y=df['volume'],
        marker_color='royalblue',
        marker_line_color='blue',
        marker_line_width=0.4,
        opacity=0.95,
        name='Volumen'
    ), row=2, col=1)

    # === Nivel 0: extremos conectados (línea blue) ===
    if extremos_df is not None:
        extremos_df['date'] = df.loc[extremos_df['index'], 'date'].values
        fig.add_trace(go.Scatter(
            x=extremos_df['date'],
            y=extremos_df['value'],
            mode='lines+markers',
            line=dict(color='rgba(65, 105, 225, 0.4)', width=1),
            marker=dict(size=8),
            text=extremos_df['type'],
            hovertemplate='Nivel 0 %{text}<br>%{x}<br>%{y:.2f}<extra></extra>',
            name='Nivel 0'
        ), row=1, col=1)

    # === Nivel 1: extremos conectados (línea black) ===
    if extremos_df_lvl1 is not None:
        extremos_df_lvl1['date'] = df.loc[extremos_df_lvl1['index'], 'date'].values
        fig.add_trace(go.Scatter(
            x=extremos_df_lvl1['date'],
            y=extremos_df_lvl1['value'],
            mode='lines+markers',
            line=dict(color='black', width=2),
            marker=dict(size=8),
            text=extremos_df_lvl1['type'],
            hovertemplate='Nivel 1 %{text}<br>%{x}<br>%{y:.2f}<extra></extra>',
            name='Nivel 1'
        ), row=1, col=1)

    # === Dibujar líneas horizontales de clúster guardian ===
    if guardian_lines:
        for line in guardian_lines:
            fig.add_shape(
                type='line',
                x0=line['x0'], x1=line['x1'],
                y0=line['y'], y1=line['y'],
                xref='x', yref='y',
                line=dict(color='red', width=1.5, dash='solid'),
                name=line['tag']
            )

            # (opcional) etiqueta
            fig.add_annotation(
                x=line['x0'],
                y=line['y'],
                text=line['tag'],
                showarrow=False,
                yshift=8,
                font=dict(size=8, color="red"),
                opacity=0.7
            )

    # === Dibujar triángulos verdes en los puntos de entrada de guardian ===
    if guardian_summary is not None:
        entry_x = df.loc[guardian_summary['min_index'], 'date'].values
        entry_y = guardian_summary['entry_price'].values
        entry_tags = guardian_summary['tag'].values  # etiquetas tipo cluster_XX

        fig.add_trace(go.Scatter(
            x=entry_x,
            y=entry_y,
            text=entry_tags,  # incluir tags
            mode='markers',
            marker=dict(
                color='green',
                size=7,
                symbol='triangle-up',
                line=dict(width=1, color='green')
            ),
            name='Limit Order',
            hovertemplate='Limit Order %{text}<br>%{x}<br>%{y:.2f}<extra></extra>'
        ), row=1, col=1)


    # === MARCAR ENTRADAS FAKE BO COMO TRIÁNGULOS VERDES ===
    if tracking_record_buy_fake_bo is not None and not tracking_record_buy_fake_bo.empty:
        fig.add_trace(go.Scatter(
            x=tracking_record_buy_fake_bo['entry_time'],
            y=tracking_record_buy_fake_bo['entry_price'],
            text=tracking_record_buy_fake_bo['tag'],  # Asegúrate de tener esta columna
            mode='markers',
            marker=dict(
                symbol='triangle-up',
                size=14,
                color='green',
                line=dict(width=1, color='darkgreen')
            ),
            name='Entradas Guardian',
            hovertemplate='Order Filled: Entry %{text}<br>%{x|%H:%M:%S}<br>%{y:.2f}<extra></extra>'
        ), row=1, col=1)


    # Layout general
    fig.update_layout(
        title=f'{symbol}_{timeframe} - {date_str}- Market Structure',
        width=1600,
        height=800,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12),
        template='plotly_white',
        showlegend=False,
        xaxis=dict(
            type='date',
            tickformat="%H:%M",
            dtick=14 * 60 * 1000,
            tickangle=0,
            showgrid=False,
            linecolor='gray',
            linewidth=1,
            rangeslider_visible=False
        ),
        xaxis2=dict(
            type='date',
            tickformat="%H:%M",
            tickangle=45,
            showgrid=False,
            linecolor='gray',
            linewidth=1
        ),
        yaxis=dict(showgrid=True, linecolor='gray', linewidth=1),
        yaxis2=dict(showgrid=True, linecolor='gray', linewidth=1)
    )

    # Exportar
    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")
    webbrowser.open('file://' + os.path.realpath(html_path))
