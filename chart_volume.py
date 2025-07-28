import os
import webbrowser
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_close_and_volume(symbol, timeframe, df, date_str, tops=None, bottoms=None,extremos_df=None, extremos_df_lvl1=None):

 
    html_path = f'charts/close_vol_chart_{symbol}_{timeframe}_{date_str}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)


    # Crear figura
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.02,
    )

    fig.add_trace(go.Candlestick(
        x=df['date'],
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        increasing_line_color='rgba(34, 200, 34, 0.13)',  
        decreasing_line_color='rgba(255, 0, 0, 0.13)',  
        increasing_fillcolor='rgba(0, 255, 0, 0.13)',
        decreasing_fillcolor='rgba(255, 0, 0, 0.13)',
        name='Velas'
    ), row=1, col=1)


    # === Dibujar línea que une los extremos (tops y bottoms alternados) ===
    if extremos_df is not None:
        x_line = df.iloc[extremos_df['index']].date
        y_line = extremos_df['value']

        fig.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            line=dict(color='blue', width=1, dash='solid'),  # puedes personalizar color/estilo
            name='Línea de extremos',
            hovertemplate='%{x}<br>%{y:.2f}<extra></extra>',
        ), row=1, col=1)



    # === Dibujar línea que une los extremos (tops y bottoms alternados) ===
    if extremos_df is not None:
        x_line = df.iloc[extremos_df_lvl1['index']].date
        y_line = extremos_df_lvl1['value']

        fig.add_trace(go.Scatter(
            x=x_line,
            y=y_line,
            mode='lines',
            line=dict(color='black', width=2, dash='solid'),  # puedes personalizar color/estilo
            name='Línea de extremos',
            hovertemplate='%{x}<br>%{y:.2f}<extra></extra>',
        ), row=1, col=1)

    '''

    # Traza de precio
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        mode='lines',
        line=dict(color='grey', width=1),
        name='Close'
    ), row=1, col=1)

  
    # Traza de low - ATR fijo
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['atr_trigger_high'],
        mode='lines',
        line=dict(color='green', width=1, dash='dot'),
        name='Low - ATR'
    ), row=1, col=1)

    # Traza de low - ATR fijo
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['atr_trigger_low'],
        mode='lines',
        line=dict(color='red', width=1, dash='dot'),
        name='Low - ATR'
    ), row=1, col=1)

    '''

    # Traza de volumen
    fig.add_trace(go.Bar(
        x=df['date'],
        y=df['volume'],
        marker_color='royalblue',
        marker_line_color='blue',
        marker_line_width=0.4,
        opacity=0.95,
        name='Volumen'
    ), row=2, col=1)

    # Traza linea vertical
    fecha_linea = pd.to_datetime(f"{date_str} 15:30:00")

    fig.add_shape(
        type="line",
        x0=fecha_linea,
        y0=0,
        x1=fecha_linea,
        y1=1,
        xref='x',
        yref='paper',
        line=dict(color="grey", width=0.2, dash="solid"),
    )

    # === Añadir puntos verdes en los tops confirmados ===
    if tops:
        top_x = [df.iloc[i].date for i, _ in tops]
        top_y = [value for _, value in tops]

        fig.add_trace(go.Scatter(
            x=top_x,
            y=top_y,
            mode='markers',
            marker=dict(color='blue', size=8, symbol='circle'),
            name='Tops confirmados',
            hovertemplate='Top<br>%{x}<br>%{y:.2f}<extra></extra>'
        ), row=1, col=1)

    # === Añadir puntos rojos en los bottoms confirmados ===
    if bottoms:
        bottom_x = [df.iloc[i].date for i, _ in bottoms]
        bottom_y = [value for _, value in bottoms]

        fig.add_trace(go.Scatter(
            x=bottom_x,
            y=bottom_y,
            mode='markers',
            marker=dict(color='blue', size=8, symbol='circle'),
            name='Bottoms confirmados',
            hovertemplate='Bottom<br>%{x}<br>%{y:.2f}<extra></extra>'
        ), row=1, col=1)



    # Layout
    fig.update_layout(
        dragmode='pan',
        title=f'{symbol}_{timeframe} - {date_str}',
        width=1600,
        height=800,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12, color="black"),
        plot_bgcolor='rgba(255,255,255,0.05)',
        paper_bgcolor='rgba(240,240,240,0.2)',
        showlegend=False,
        template='plotly_white',
        xaxis=dict(
            type='date',
            tickformat="%H:%M",
            dtick=14 * 60 * 1000,  # 15 minutos
            tickangle=0,
            showgrid=False,
            linecolor='gray',
            linewidth=1,
            rangeslider_visible=False
        ),
        xaxis2=dict(
            type='date',
            tickformat="%H:%M",
            dtick=14 * 60 * 1000,
            tickangle=45,
            showgrid=False,
            linecolor='gray',
            linewidth=1
        ),
        yaxis=dict(showgrid=True, linecolor='gray', linewidth=1),
        yaxis2=dict(showgrid=True, linecolor='grey', linewidth=1),
    )
    # Guardar HTML
    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")

    # Abrir en navegador
    webbrowser.open('file://' + os.path.realpath(html_path))
