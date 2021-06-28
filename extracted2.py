import twitter
import os
import tweepy as tw
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from tweepy import API

# Set the Twitter API authentication
api = twitter.Api(consumer_key='eTwR2lbd6dMxCq988wtWnBvGC',
                  consumer_secret='IEsaSATulZcZyBE6QWxzK97dBU12wB7ORbVBk7kqUrYZNTfOxM',
                  access_token_key='1404645710058987522-2tHLCZnMazsLg86yBKL3s5ZUrHX6hB',
                  access_token_secret='B1YbGzAFbRrAOhLS1867uJIVza30v4GLifQIOb7gA04Cm')

# These are the accounts for which you will fetch data
# It's a list of lists, with a category added for each handle
handles_list = [
    ['aoc', 'BernieSanders'],
    ['SenSchumer', 'ewarren'],
    ['LeaderMcConnell', 'SenGillibrand']
]

# Function to add row to accounts table
def insert_db(handle, category, followers, description):
    conn = sqlite3.connect('mike_dcd.db')
    cur = conn.cursor()
    cur.execute('''
        INSERT INTO twaccounts VALUES (?,?,?,?,?);
        ''', (datetime.now(), handle, category, followers, description))
    conn.commit()
    conn.close()



# Create the table if it's not in the db
conn = sqlite3.connect('mike_dcd.db')
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS twaccounts
    (FetchDate Date, Handle Text, Category Text, Followers Integer, Description Text)
    ''')
conn.commit()
conn.close()

#Iterate over handles and hit the API with each
for handle in handles_list:
    print ('Fetching @' + handle[0])
    try:
        user = api.GetUser(screen_name=handle[2])
        followers = user.GetFollowersCount()
        description = user.GetDescription()
        insert_db(handle[0], category[0], followers, description)
    except:
        print ('-- ' + handle[0] + ' not found')