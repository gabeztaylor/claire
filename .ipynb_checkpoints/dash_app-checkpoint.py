from dash import Dash, html, dcc, dash_table
import plotly.express as px
import pandas as pd
import dash_helpers as dh
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output, State
from random import randint
import re
import dash_daq as daq
import os
import base64


app = Dash(__name__, external_stylesheets=[dbc.themes.LUX])

##########################
# Read in Data and Clean #
##########################

# df = pd.read_csv('../Claire/Messages - Claire Robinson.csv')
df = pd.read_csv('s3://claireandgabriel1year.com/Messages - Claire Robinson.csv')
df['Message Date'] = df['Message Date'].apply(pd.to_datetime)
df['Day'] = df['Message Date'].dt.date
df['Time'] = df['Message Date'].dt.time
df['Hour'] = df['Message Date'].dt.hour
df['Type'] = df['Type'].apply(lambda x: 'Claire' if x == 'Incoming' else 'Gabe')
df.Text = df.Text.apply(lambda x: re.sub('“.*?”', '', x) if not pd.isnull(x) else x)

##########################
# Pics ###################
##########################

pictures = os.listdir('assets')
pictures.remove('.ipynb_checkpoints')


##########################
# Figs ###################
##########################

day_ts_fig = dh.plot_by_day(df)
hour_ts_fig = dh.plot_by_hour(df)
word_tbl = dh.words_table(df)
txt_dist, wd_dist = dh.text_length(df)
emots_fig, emots_df = dh.emoji_cnt(df)
ngrams_fig = dh.ngram_cnt(df)
#############################

#############################
# Stats #####################
#############################
n_txts = len(df)
wrd_hnt = dh.n_games(df)
qck_stats = dh.get_stats(df)

#############################
# Data Tables ###############
#############################

stats_table = dbc.Table.from_dataframe(qck_stats, striped=True, bordered=True, hover=True, index=False, size = 'sm',
                                      style = {'font-size' : '20px', 'text-align' : 'center'})

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
    
    html.Br(),
    
    html.Br(),
    
    html.Div([dbc.Col([html.P(id = 'random-text', style={'vertical-align' : 'center', 'display' : 'inline-block', "margin-left": "50px"})]),
              dcc.Interval(id='interval-component1', interval=20000, n_intervals=0),
              
              dbc.Col([html.H3('Some Quick Stats', style = {'text-align' : 'center'}),
                      html.Div([stats_table])]),
              
              dbc.Col([html.H3('How do we look?', style = {'text-align' : 'center'}),
                       html.Div([html.Img(id='random-pic')],  style = {'display': 'block', 'marginLeft': 'auto' ,
                                                                       'marginRight': 'auto', 'width' : '50%'})]),
              dcc.Interval(id='interval-component2', interval=20000, n_intervals=0)
             ], style = {'display' : 'flex'}),
    
    html.Br(),
    
    html.Br(),
    
    
    html.Div([
        dbc.Col([html.H3('Our Total Texts per Day'),
                 html.P("Choose number of smoothing days: "),
                 daq.Slider(min=1, max=365, step=1, value=1, id='smoothing-param', size = 150),
                 html.P(id='smooth-text'),
                 dcc.Graph(figure = day_ts_fig,id="txt-by-day", style = {'display' : 'inline-block', "margin-left": "15px"}),]),
        dbc.Col([html.H3('Our Total Words per Day'),
                 dcc.Graph(figure = wd_dist, id="wd-dist-fig", style = {'display' : 'inline-block'})
                ])
            ], style = {'display' : 'flex', "margin-left": "50px", "margin-left": "50px"}),
    
    html.Br(),
    
    html.Div([dbc.Col([html.H3('Our Total Texts by Hour'),
                       dcc.Graph(figure = hour_ts_fig, id="txt-by-hour", style = {'display' : 'inline-block'})
                      ]),
              
              dbc.Col([html.H3('Number of Words per Text'),
                       dcc.Graph(figure = txt_dist, id="txt-len-dist", style = {'display' : 'inline-block'})
                      ])
             ], style = {'display' : 'flex', "margin-left": "50px", "margin-left": "50px"}),
    
    html.Br(),
    
    html.Div([dbc.Col([dbc.Spinner([html.Div([
                html.Div([html.H3('Our Favorite Words'),
                          html.P("Choose N:"), 
                          dcc.Input(id='ngram', type='number', value = 1, min=1, max=5, step=1, debounce = True)
                         ], style = {'display' : 'inline-block'}),
                html.Div([html.P("Choose Stop Words:"),
                        dcc.Input(id='stops', value = 'word hunt reversi 20 questions', debounce = True, placeholder = "seperate with spaces")
                         ], style = {'display' : 'inline-block', "margin-left": "15px"}),
                html.Div([dcc.Graph(figure = ngrams_fig, id="ngrams-fig", style = {'display' : 'inline-block'}),
                        ])])])
                    ]),
        
            dbc.Col([html.H3('Our Favorite Emojis'),
                     dcc.Graph(figure = emots_fig, id="emot-fig", style = {'display' : 'inline-block'})
                    ])
                ], style = {'display' : 'flex', "margin-left": "50px", "margin-left": "50px"})
])


@app.callback(
    Output('random-text', 'children'),
    Input('interval-component1', 'n_intervals')
)
def sample_text(n):
    randi = randint(0, len(df) - 1)
    
    text = df.iloc[randi:(randi+10), : ]
    date = text.Day.iloc[0]
    final = [html.H3(f'What did we say on {date}?', style = {'text-align' : 'center'}), html.Br()]
    
    for i in text.index:
        txt = text.loc[i, 'Text']
        sender = text.loc[i, 'Type']
        final += [html.Strong(f"{sender}: "), html.Span(f"{txt}"), html.Br()]
        
    return final

@app.callback(
    Output('random-pic', 'src'),
    Input('interval-component1', 'n_intervals'))
def update_image_src(n):
    # print the image_path to confirm the selection is as expected
    randi = randint(0, len(pictures) - 1)
    
    image_path = f"assets/{pictures[randi]}"
    print('current image_path = {}'.format(image_path))
    encoded_image = base64.b64encode(open(image_path, 'rb').read())
    return 'data:image/png;base64,{}'.format(encoded_image.decode())


@app.callback(
    Output('txt-by-day', 'figure'),
    Output('smooth-text', 'children'),
    Input('smoothing-param', 'value')
)
def adjust_smoothing(s):
    fig = dh.plot_by_day(df, s)
    s_text = f'You have chosen: {s} days'
    return fig, s_text

@app.callback(
    Output('ngrams-fig', 'figure'),
    Input('ngram', 'value'),
    Input('stops', 'value')
)
def choose_ngram(n, stops):
    print(stops)
    stop_words = stops.split()
    fig = dh.ngram_cnt(df, n, stop_words)
    return fig

app.run_server(debug=True)
# app.run_server(host='0.0.0.0', port=8050)
