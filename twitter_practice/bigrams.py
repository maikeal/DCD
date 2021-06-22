import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import itertools
import collections
from datetime import datetime, timedelta

import tweepy as tw
import nltk
from nltk import bigrams
from nltk.corpus import stopwords
import re
import networkx as nx

import warnings
warnings.filterwarnings("ignore")

sns.set(font_scale=1.5)
sns.set_style("whitegrid")

consumer_key= 'aa5xPHnUlFIVJrMb0QuCSAMFk'
consumer_secret= 'CsatdSlbLXm4bUiJLKa4ZpDYBxkNEpdYq2zZL3jlaRf1U5VmyF'
access_token= '1401632059752435717-msitAGNwn4n9Q8ddVk4V0E4eFhVrve'
access_token_secret= 'StkY7ZMvFF21UYRjc1kXbOBtCans0xuBR53Frw4fGx9DM'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

search_term = "#BlackLivesMatter -filter:retweets"
date_since = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

print("before")
tweets = tw.Cursor(api.search, q=search_term, lang="en", since=date_since).items(500)
print("after 1")

# get_bios
bios = [tweet.user.description for tweet in tweets]

# Create a sublist of lower case words for each tweet
words_in_bio = [bio.lower().split() for bio in bios]

# Download stopwords
nltk.download('stopwords')
stop_words = set(stopwords.words('english'))
#print("after 2")

# Remove stop words from each tweet list of words
bios_nsw = [[word for word in bio_words if not word in stop_words]
              for bio_words in words_in_bio]

terms_bigram = [list(bigrams(bio)) for bio in bios_nsw]

#print(terms_bigram[0])
#print(tweets_no_urls[0])

# Flatten list of bigrams in clean tweets
bigrams = list(itertools.chain(*terms_bigram))

# Create counter of words in clean bigrams
bigram_counts = collections.Counter(bigrams)

#print(bigram_counts.most_common(20))

bigram_df = pd.DataFrame(bigram_counts.most_common(20),
                             columns=['bigram', 'count'])

#print(bigram_df)

# Create dictionary of bigrams and their counts
d = bigram_df.set_index('bigram').T.to_dict('records')

G = nx.Graph()

# Create connections between nodes
for k, v in d[0].items():
    G.add_edge(k[0], k[1], weight=(v * 10))

fig, ax = plt.subplots(figsize=(10, 8))

pos = nx.spring_layout(G, k=2)

# Plot networks
nx.draw_networkx(G, pos,
                 font_size=16,
                 width=3,
                 edge_color='grey',
                 node_color='purple',
                 with_labels = False,
                 ax=ax)

# Create offset labels
for key, value in pos.items():
    x, y = value[0]+.135, value[1]+.045
    #x, y = value[0], value[1]
    ax.text(x, y,
            s=key,
            bbox=dict(facecolor='red', alpha=0.25),
            horizontalalignment='center', fontsize=13)
    
plt.show()