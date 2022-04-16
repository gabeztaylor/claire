from dash import Dash, html, dcc, dash_table
import plotly.express as px
import pandas as pd
import dash_helpers as dh
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
from random import randint
import re

app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

##########################
# Read in Data and Clean #
##########################

df = pd.read_csv('/Users/gabrieltaylor/Downloads/Messages - Claire Robinson.csv')
df['Message Date'] = df['Message Date'].apply(pd.to_datetime)
df['Day'] = df['Message Date'].dt.date
df['Time'] = df['Message Date'].dt.time
df['Hour'] = df['Message Date'].dt.hour
df['Type'] = df['Type'].apply(lambda x: 'Claire' if x == 'Incoming' else 'Gabe')
df.Text = df.Text.apply(lambda x: re.sub('“.*?”', '', x) if not pd.isnull(x) else x)


##########################
# Figs ###################
##########################

day_ts_fig = dh.plot_by_day(df)
hour_ts_fig = dh.plot_by_hour(df)
word_tbl = dh.words_table(df)
txt_dist = dh.text_length(df)
#############################

#############################
# Stats #####################
#############################
n_txts = len(df)
wrd_hnt = dh.n_games(df)
emots_fig, emots_df = dh.emoji_cnt(df)
print(emots_df)


#############################
# Data Tables ###############
#############################

corpus_datatable = dash_table.DataTable(
    id='wordtbl-table',
    data=word_tbl.to_dict('records'),
    columns = [{'id': c, 'name': c} for c in word_tbl.columns],
    style_table={
        'overflowY': 'scroll',
        'overflowX': 'scroll',
        'float' : 'right'
        },
    style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0
    },
    tooltip_data=[
        {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in word_tbl.to_dict('records')
    ],
    tooltip_duration=None,
    filter_action="native",
    sort_action="native",
    page_size=10
)

emots_dt = dash_table.DataTable(
    id='claire-emot-table',
    data=emots_df.to_dict('records'),
    columns = [{'id': c, 'name': c} for c in emots_df.columns],
    style_table={
        'overflowY': 'scroll',
        'overflowX': 'scroll',
        'float' : 'right'
        },
    style_cell={
        'overflow': 'hidden',
        'textOverflow': 'ellipsis',
        'maxWidth': 0
    },
    tooltip_data=[
        {column: {'value': str(value), 'type': 'markdown'} for column, value in row.items()} for row in emots_df.to_dict('records')
    ],
    tooltip_duration=None,
    filter_action="native",
    sort_action="native",
    page_size=10
)



app.layout = html.Div(children=[
    html.H1(children='Happy 1 Year* of dating!', style = {'text-align' : 'center'}),
    
    html.H3(children=f'{n_txts:,} Texts! {wrd_hnt:,} word hunt games! and lots of love ❤️', style = {'text-align' : 'center'}),

    html.Div(children='*(2 months and one week)', style = {'text-align' : 'center'}),
    
    html.Div(children=[
        dcc.Graph(figure = day_ts_fig, id="graph1", style = {'display' : 'inline-block'}),
        dcc.Graph(figure = hour_ts_fig, id="graph2", style = {'display' : 'inline-block'}),
        dcc.Graph(figure = txt_dist, id="graph3", style = {'display' : 'inline-block'}),
        dcc.Interval(
            id='interval-component',
            interval=30000, # in milliseconds
            n_intervals=0)
    ], style = {'display' : 'flex'}),
    
    html.Div(children=[
    html.P(id = 'random-text', style={'background-image': 'url(/assets/txt_bubble.png)',
                                      'width': '500px', 'height' : '350px', 'text-align' : 'center', 'vertical-align' : 'center'}),
    html.Div([corpus_datatable]),
    html.Div([emots_dt]),
    dcc.Graph(figure = emots_fig, id="graph4", style = {'display' : 'inline-block'}),
    ], style = {'display' : 'flex'})
])


@app.callback(
    Output('random-text', 'children'),
    Input('interval-component', 'n_intervals')
)
def sample_text(n):
    randi = randint(0, len(df))
    
    text = df.iloc[randi:(randi+10), : ]
    date = text.Day.iloc[0]
    final = [f'Date: {date}', html.Br()]
    
    for i in text.index:
        txt = text.loc[i, 'Text']
        sender = text.loc[i, 'Type']
        final += [f"{sender}: {txt}", html.Br()]
        
    return final

app.run_server(debug=True)

