import sqlalchemy as sa
import datetime as dt
import time 
from dash import Dash, html, dash_table,  dcc,  Input, Output
import pandas as pd


def update():

    engine = sa.create_engine(
        "postgresql+psycopg2://postgres:ashwin@localhost:5432/cronos",
        echo=False,
    )

    df = pd.read_sql('tweets', engine,)

    df = df.sort_values('posted_time').drop_duplicates(subset=['tweet_id'], keep='last')
    df['alive_horas'] = df['alive'].str.split(':').str[0]
    df['alive_horas'] = df['alive_horas'].astype(int)
    df = df.sort_values(by=['alive_horas'], ascending=True)

    fecha_actual = pd.Timestamp.now(tz='America/Mexico_City').date()
    df = df[df['posted_time'].dt.date == fecha_actual]
    df['tweet_url'] = df['tweet_url'].apply(lambda x: f"[url]({x})")

    df['hashtags'] = df['hashtags'].replace(r'\{|\}', '', regex=True)

    return df   

df = update() 

timer = 40
fecha_inicio = dt.datetime.now()


app = Dash(__name__)

app.layout = html.Div([
    
    html.H1('Cronos Twitter'),
    dcc.Interval(
        id='interval_component',
        interval=1*1000, # in milliseconds
        n_intervals=0
    ),
    html.Div(id='cuenta_regresiva'),

    dash_table.DataTable(

        id='tabla',
        columns=[
            {'name': 'Tweet_id', 'id': 'tweet_id'},
            {'name': 'Usuario', 'id': 'username'},
            {'name': 'Respuestas', 'id': 'replies'},
            {'name': 'Retweets', 'id': 'retweets'},
            {'name': 'Likes', 'id': 'likes'},
            {'name': 'Horas', 'id': 'alive_horas'},
            {'name': 'Vivo', 'id': 'alive'},
            {'name': 'Contenido', 'id': 'content',},
            {'name': 'Hashtags', 'id': 'hashtags'},
            {'name': 'Menciones', 'id': 'mentions'},
            {'name': 'Tweet_url', 'id': 'tweet_url', 'presentation': 'markdown'},
            
        

        ],
        
        data=df.to_dict('records'),
        row_selectable='single',
        selected_rows=[],
        style_data_conditional = [
    {
        'if': {
            'filter_query': '{alive_horas} <= 0',
        },
        'backgroundColor': '#28B463',
        'color': 'black',
    },
    {
        'if': {
            'filter_query': '{alive_horas} >= 1 && {alive_horas} <= 3',
        },
        'backgroundColor': '#D4AC0D',
        'color': 'black',
    },
    {
        'if': {
            'filter_query': '{alive_horas} > 3',
        },
        'backgroundColor': '#CB4335',
        'color': 'black',
    }
],
        
        style_cell={
            'whiteSpace': 'normal',
            'height': 'auto',
            'minWidth': '150px',
            'width': '400px',
            'maxWidth': '600px',
            'textAlign': 'center',
            },
        style_header={'backgroundColor': 'lightblue', 'fontWeight': 'bold'},
        style_data={'backgroundColor': 'lightgrey', 'color': 'black'},
        #sort_action='native',        
        page_action='native',
        filter_action='native',


    ),




])

def df():
    df = update()
    return df

#callbacks
@app.callback(Output('tabla', 'data'),
          Input('interval_component', 'n_intervals'))

def update_cuenta_regresiva(n):
    df = update()
    time.sleep(1000)
    return df.to_dict('records')





if __name__ == '__main__':
    app.run(debug=True)