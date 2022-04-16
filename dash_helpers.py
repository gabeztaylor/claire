import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import emoji
import regex

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
    fig.update_layout(
        xaxis = dict(
            tickmode = 'linear'
    )
)
    return fig

def word_cnt(x):
    corp = x['Text'].str.cat(sep=' ')
    corp = [i.lower() for i in corp.split()]
    return pd.Series(dict(Counter(corp).most_common()))

def words_table(df):
    cnts = df.groupby('Type').apply(word_cnt).reset_index()
    cnts.columns = ['person', 'word', 'count']
    
    return cnts.sort_values('count', ascending = False)

def text_length(df):
    plot_df = df.copy()
    plot_df['length'] = plot_df.Text.fillna('').apply(lambda x: x.split()).apply(len)
    plot_df = plot_df.loc[plot_df.Type != 'Notification', :].reset_index()
    plot_df = plot_df.groupby(['Type', 'length']).apply(lambda x: len(x)).reset_index().rename(columns = {0: 'count'})

    fig = px.bar(plot_df, x="length", y="count",
             color="Type", barmode = 'group')
    
    fig.update_layout(xaxis_range=[-2,20])
    
    return fig

def n_games(df):
    return df.Text.fillna('').apply(lambda x: 'word hunt' in ' '.join([i.lower() for i in x.split()])).sum()

##########
# Emojis #
##########

def split_count(text):

    emoji_list = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI['en'] for char in word):
            emoji_list.append(word)
    
    return emoji_list

def emoji_cnt(df):
    claire_corpus = df.loc[df.Type == 'Claire', 'Text'].str.cat(sep=' ')
    claire_corpus = [i.lower() for i in claire_corpus.split()]
    
    gabe_corpus = df.loc[df.Type == 'Gabe', 'Text'].str.cat(sep=' ')
    gabe_corpus = [i.lower() for i in gabe_corpus.split()]
    
    stop_emots = ['🟨', '🟩', '⬛', '', '  ']
    
    ### Claire
    emojies = split_count(' '.join(claire_corpus))
    claire_emojis = ' '.join(emoji for emoji in emojies if emoji not in stop_emots)
    claire_emojis = pd.DataFrame(dict(Counter(claire_emojis.split()).most_common()), index = range(1)).transpose().reset_index()
    claire_emojis = claire_emojis.rename(columns = {'index' : 'emoji', 0 : 'n'})
    claire_emojis['person'] = 'Claire'
    
    ### Gabe
    emojies = split_count(' '.join(gabe_corpus))
    gabe_emojis = ' '.join(emoji for emoji in emojies if emoji not in stop_emots)
    
    gabe_emojis = pd.DataFrame(dict(Counter(gabe_emojis.split()).most_common()), index = range(1)).transpose().reset_index()
    gabe_emojis = gabe_emojis.rename(columns = {'index' : 'emoji', 0 : 'n'})
    gabe_emojis['person'] = 'Gabe'
    
    emot_df = claire_emojis.append(gabe_emojis)
    
    plot_df = claire_emojis.sort_values(by = 'n', ascending = False).iloc[:10, :]\
                           .append(gabe_emojis.sort_values(by = 'n', ascending = False).iloc[:10, :])
    
    fig = px.bar(plot_df, x="emoji", y="n", color="person", barmode = 'group')
    
    return fig, emot_df
    
    
    
