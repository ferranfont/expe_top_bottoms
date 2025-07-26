import os
import webbrowser
import pandas as pd
import plotly.graph_objs as go
from plotly.subplots import make_subplots

def plot_close_and_volume(symbol, timeframe, df, date_str):
    # Crear carpeta si no existe
    html_path = f'charts/close_vol_chart_{symbol}_{timeframe}_{date_str}.html'
    os.makedirs(os.path.dirname(html_path), exist_ok=True)

    # Normalizar columnas
    df = df.rename(columns=str.lower)

    # Convertir columna 'date' a datetime si no lo es
    if not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df['date'])

    df = df.sort_values('date')

    # Crear figura
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        row_heights=[0.80, 0.20],
        vertical_spacing=0.03,
    )

    # Traza de precio
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['close'],
        mode='lines',
        line=dict(color='blue', width=1.5),
        name='Close'
    ), row=1, col=1)

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

    # Layout
    fig.update_layout(
        dragmode='pan',
        title=f'{symbol}_{timeframe} - {date_str}',
        width=1500,
        height=700,
        margin=dict(l=20, r=20, t=40, b=20),
        font=dict(size=12, color="black"),
        plot_bgcolor='rgba(255,255,255,0.05)',
        paper_bgcolor='rgba(240,240,240,0.1)',
        showlegend=False,
        template='plotly_white',
        xaxis=dict(
            type='date',
            tickformat="%H:%M",
            dtick=15 * 60 * 1000,  # 2 minutos
            tickangle=0,
            showgrid=False,
            linecolor='gray',
            linewidth=1
        ),
        yaxis=dict(showgrid=True, linecolor='gray', linewidth=1),
        xaxis2=dict(
            type='date',
            tickformat="%H:%M",
            dtick=15 * 60 * 1000,
            tickangle=45,
            showgrid=False,
            linecolor='gray',
            linewidth=1
        ),
        yaxis2=dict(showgrid=True, linecolor='grey', linewidth=1),
    )
    # Guardar HTML
    fig.write_html(html_path, config={"scrollZoom": True})
    print(f"✅ Gráfico Plotly guardado como HTML: '{html_path}'")

    # Abrir en navegador
    webbrowser.open('file://' + os.path.realpath(html_path))
