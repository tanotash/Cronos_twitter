import sqlalchemy as sa
import datetime as dt
from dash import Dash, html, dash_table, dcc, Input, Output, State
import pandas as pd
import os
from dotenv import load_dotenv
import dash_bootstrap_components as dbc  # Bootstrap para mejor diseño

load_dotenv()

# Función para obtener y procesar datos de la base de datos
def update():
    """
    Obtiene y procesa los tweets desde la base de datos.

    Returns:
        pandas.DataFrame: Datos procesados de los tweets.
    """
    engine = sa.create_engine(str(os.getenv("CONEXION")), echo=False)
    df = pd.read_sql('tweets', engine)

    df = df.sort_values('posted_time').drop_duplicates(subset=['tweet_id'], keep='last')
    df['alive_horas'] = df['alive'].str.split(':').str[0].astype(int)
    df = df.sort_values(by=['alive_horas'], ascending=True)

    fecha_actual = pd.Timestamp.now(tz='America/Mexico_City').date()
    df = df[df['posted_time'].dt.date == fecha_actual]

    df['tweet_url'] = df['tweet_url'].apply(lambda x: f"[Ver Tweet]({x})")
    df['hashtags'] = df['hashtags'].replace(r'\{|\}', '', regex=True)

    return df

# Tiempo de actualización
TIMER = 40  # Segundos

# Inicializar la app con Bootstrap
app = Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# Layout con mejor diseño
app.layout = dbc.Container([
    dcc.Store(id='fecha_inicio', data=str(dt.datetime.now())),  # Guardar fecha de inicio dinámicamente

    dbc.Row([
        dbc.Col(html.H1('Cronos Twitter', className="text-center text-primary mt-4"), width=12),
    ]),

    dbc.Row([
        dbc.Col(html.H5("Cuenta regresiva para actualización:", className="text-center"), width=12),
        dbc.Col(html.H3(id='cuenta_regresiva', className="text-center text-danger"), width=12),
    ]),

    dbc.Row([
        dbc.Col([
            dash_table.DataTable(
                id='tabla',
                columns=[
                    {'name': 'Tweet ID', 'id': 'tweet_id'},
                    {'name': 'Usuario', 'id': 'username'},
                    {'name': 'Respuestas', 'id': 'replies'},
                    {'name': 'Retweets', 'id': 'retweets'},
                    {'name': 'Likes', 'id': 'likes'},
                    {'name': 'Horas', 'id': 'alive_horas'},
                    {'name': 'Vivo', 'id': 'alive'},
                    {'name': 'Contenido', 'id': 'content'},
                    {'name': 'Hashtags', 'id': 'hashtags'},
                    {'name': 'Menciones', 'id': 'mentions'},
                    {'name': 'Tweet URL', 'id': 'tweet_url', 'presentation': 'markdown'},
                ],
                data=update().to_dict('records'),
                style_data_conditional=[
                    {'if': {'filter_query': '{alive_horas} <= 0'}, 'backgroundColor': '#28B463', 'color': 'white'},
                    {'if': {'filter_query': '{alive_horas} >= 1 && {alive_horas} <= 3'}, 'backgroundColor': '#D4AC0D', 'color': 'black'},
                    {'if': {'filter_query': '{alive_horas} > 3'}, 'backgroundColor': '#CB4335', 'color': 'white'},
                ],
                style_cell={
                    'whiteSpace': 'normal', 'height': 'auto', 'minWidth': '120px', 'width': '200px', 'maxWidth': '300px',
                    'textAlign': 'center', 'padding': '10px'
                },
                style_header={'backgroundColor': 'navy', 'color': 'white', 'fontWeight': 'bold'},
                style_data={'backgroundColor': '#f8f9fa', 'color': 'black'},
                page_action='native',
                page_size=10,
                fixed_rows={'headers': False},
                )
        ], width=12),
    ]),

    # Intervalo para actualizar datos cada 1 segundo
    dcc.Interval(id='interval_component', interval=1000, n_intervals=0),
], fluid=True)

# Callback para actualizar la tabla y la cuenta regresiva
@app.callback(
    [Output('tabla', 'data'), Output('cuenta_regresiva', 'children'), Output('fecha_inicio', 'data')],
    [Input('interval_component', 'n_intervals')],
    [State('fecha_inicio', 'data')]
)
def update_data(n, fecha_inicio_str):
    """
    Actualiza los datos de la tabla y muestra la cuenta regresiva.

    Parameters:
        n (int): Número de intervalos.
        fecha_inicio_str (str): Fecha de inicio almacenada.

    Returns:
        list: Datos actualizados, tiempo restante y nueva fecha de inicio.
    """
    fecha_inicio = dt.datetime.fromisoformat(fecha_inicio_str)
    tiempo_transcurrido = (dt.datetime.now() - fecha_inicio).total_seconds()
    tiempo_restante = max(0, TIMER - int(tiempo_transcurrido))

    if tiempo_restante == 0:
        df = update()
        nueva_fecha_inicio = dt.datetime.now().isoformat()  # Reiniciar el contador
        return df.to_dict('records'), "Actualizando...", nueva_fecha_inicio

    return update().to_dict('records'), f"{tiempo_restante} segundos", fecha_inicio_str

# Ejecutar la app
if __name__ == '__main__':
    app.run(debug=True)
