import pandas as pd
import numpy as np
from collections import Counter
import plotly.express as px
import plotly.graph_objects as go
import plotly.figure_factory as ff
import emoji
import regex
import re
from nltk.util import ngrams

def plot_by_day(df, smooth = 1):

    plot_df = df.groupby(['Day', 'Type'])\
                .apply(len).ewm(span = smooth)\
                .mean()\
                .reset_index()\
                .rename(columns = {0: 'smoothed count'})
    
    fig = px.line(plot_df, x='Day', y='smoothed count', color = 'Type',
                  title = 'Our Total Texts per Day',
                 color_discrete_sequence=['pink', 'blue'],
                 labels={"Type": "Lover"})
    # fig.add_trace(go.Bar(x = plot_df['Day'], y = plot_df['sum']))
    
    return fig

def plot_by_hour(df):
    plot_df = df.groupby(['Hour', 'Type'])\
                .apply(len)\
                .reset_index()\
                .rename(columns = {0: 'count'})
    
    fig = px.bar(plot_df, x='Hour', y='count', color = 'Type', title = 'Our Total Texts by Hour',
                color_discrete_sequence=['pink', 'blue'],
                labels={"Type": "Lover"})
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
    ### Drop 0 length
    plot_df = plot_df.loc[plot_df.length > 0, : ]
    
    tl_plot_df = plot_df.groupby(['Type', 'length']).apply(lambda x: len(x)).reset_index().rename(columns = {0: 'count'})

    tl_fig = px.bar(tl_plot_df, x="length", y="count",
             color="Type", barmode = 'group',
             title = 'Number of Words per Text',
             color_discrete_sequence=['pink', 'blue'],
            labels={"Type": "Lover"})
    
    tl_fig.update_layout(xaxis_range=[0,20])
    
    ### Word per day distribution
    wd_plot_df = plot_df.groupby(['Day', 'Type']).apply(lambda x: sum(x.length)).reset_index().rename(columns = {0: 'count'})
    
    wd_fig = px.histogram(wd_plot_df, x="count", color="Type",
                          title = 'Distribution of Words Texted per Day',
                         color_discrete_sequence=['pink', 'blue'],
                         labels={"Type": "Lover"})
    
    return tl_fig, wd_fig


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
    
    ### Claire Emojis
    emojies = split_count(' '.join(claire_corpus))
    claire_emojis = ' '.join(emoji for emoji in emojies if emoji not in stop_emots)
    claire_emojis = pd.DataFrame(dict(Counter(claire_emojis.split()).most_common()), index = range(1)).transpose().reset_index()
    claire_emojis = claire_emojis.rename(columns = {'index' : 'emoji', 0 : 'n'})
    claire_emojis['person'] = 'Claire'
    
    ### Gabe Emojis
    emojies = split_count(' '.join(gabe_corpus))
    gabe_emojis = ' '.join(emoji for emoji in emojies if emoji not in stop_emots)
    
    gabe_emojis = pd.DataFrame(dict(Counter(gabe_emojis.split()).most_common()), index = range(1)).transpose().reset_index()
    gabe_emojis = gabe_emojis.rename(columns = {'index' : 'emoji', 0 : 'n'})
    gabe_emojis['person'] = 'Gabe'
    
#     ### Emojis Fig
    emot_df = claire_emojis.append(gabe_emojis)
#     plot_df = claire_emojis.sort_values(by = 'n', ascending = False).iloc[:10, :]\
#                            .append(gabe_emojis.sort_values(by = 'n', ascending = False).iloc[:10, :])

    plot_df = claire_emojis.merge(gabe_emojis, on = 'emoji', how = 'outer', suffixes = ('Claire', 'Gabe'))
    plot_df = plot_df.iloc[:10, ]
    plot_df = plot_df.rename(columns = {'nClaire' : 'Claire', 'nGabe' : 'Gabe'})
    
    emot_fig = px.bar(plot_df, x="emoji", y=['Claire', 'Gabe'], barmode = 'group',
                title = 'Our Favorite Emojis', color_discrete_sequence=['pink', 'blue'],
                labels={"variable": "Lover"})
    
    
    return emot_fig, emot_df

###########
# N-Grams #
###########

def ngram_cnt(df, n = 1, stops = []):
    claire_corpus = df.loc[df.Type == 'Claire', 'Text'].str.cat(sep=' ')
    claire_corpus = [i.lower() for i in claire_corpus.split()]
    
    gabe_corpus = df.loc[df.Type == 'Gabe', 'Text'].str.cat(sep=' ')
    gabe_corpus = [i.lower() for i in gabe_corpus.split()]
    
    ### Claire N-Gram
    s = [re.sub(r'[^a-zA-Z0-9\s]', '', w) for w in claire_corpus]
    s = [w for w in s if w not in stops]
    s = ' '.join(s)
    tokens = [token for token in s.split(" ") if token != ""]
    output = list(ngrams(tokens, n))
    claire_ngram = dict(Counter(output).most_common())
    claire_ngram = pd.DataFrame(claire_ngram, index = range(1))\
                     .transpose()\
                     .reset_index()\
                     .rename(columns = {'level_0' : 'ngram', 0 : 'n'})
    
    claire_ngram['ngram'] = claire_ngram.iloc[:, :n].apply(lambda x: ' '.join(x), axis=1)
    # claire_ngram['person'] = 'Claire'
    
    ### Gabe N-Gram
    s = [re.sub(r'[^a-zA-Z0-9\s]', '', w) for w in gabe_corpus]
    s = [w for w in s if w not in stops]
    s = ' '.join(s)
    tokens = [token for token in s.split(" ") if token != ""]
    output = list(ngrams(tokens, n))
    gabe_ngram = dict(Counter(output).most_common())
    gabe_ngram = pd.DataFrame(gabe_ngram, index = range(1))\
                     .transpose()\
                     .reset_index()\
                     .rename(columns = {'level_0' : 'ngram', 0 : 'n'})
    
    gabe_ngram['ngram'] = gabe_ngram.iloc[:, :n].apply(lambda x: ' '.join(x), axis=1)
    
#     gabe_ngram['person'] = 'Gabe'
    
#     ### N-Gram Fig
#     plot_df = claire_ngram.sort_values(by = 'n', ascending = False).iloc[:10, :]\
#                            .append(gabe_ngram.sort_values(by = 'n', ascending = False).iloc[:10, :])

    plot_df = claire_ngram.merge(gabe_ngram, on = 'ngram', how = 'outer', suffixes = ('Claire', 'Gabe'))
    plot_df = plot_df.iloc[:10, ]
    plot_df = plot_df.rename(columns = {'nClaire' : 'Claire', 'nGabe' : 'Gabe'})
    
    ngram_fig = px.bar(plot_df, x="ngram", y=['Claire', 'Gabe'], barmode = 'group',
                title = 'Our Favorite Words', color_discrete_sequence=['pink', 'blue'],
                labels={"variable": "Lover"})
    
    return ngram_fig
    
    
    
    
