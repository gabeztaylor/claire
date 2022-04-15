import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go

def plot_by_day(df):
    plot_df = df.groupby(['Day', 'Type'])\
                .apply(lambda x: len(x)).reset_index()\
                .rename(columns = {0 : 'txts'})\
                .reset_index()\
                .pivot(columns = 'Type', values = 'txts', index = 'Day')\
                .reset_index()
    
    plot_df['sum'] = plot_df['Claire'] + plot_df['Gabe']
    
    fig = px.line(plot_df, x='Day', y='sum')
    # fig.add_trace(go.Bar(x = plot_df['Day'], y = plot_df['sum']))
    
    return fig

def plot_by_hour(df):
    plot_df = df.groupby('Hour').apply(lambda x: len(x)).reset_index().rename(columns = {0 : 'txts'})
    fig = px.bar(plot_df, x='Hour', y='txts')
    return fig

def word_cnt(x):
    corp = x['Text'].str.cat(sep=' ')
    corp = [i.lower() for i in corp.split()]
    return pd.Series(dict(Counter(corp).most_common()))

def words_table(df):
    cnts = df.groupby('Type').apply(word_cnt).reset_index()
    cnts.columns = ['person', 'word', 'count']
    
    return cnts.sort_values('count', ascending = False)
    
