import twitter
import os
import tweepy as tw
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
from tweepy import API

# if you make a file called constants.py and set the API keys as variables and import constants like this,
# it'll be safer than uploading our keys to Github. 
# To keep constants.py private what you do is you create a file called .gitignore and then type "constants.py" without the quotes, and then Git will ignore it
import constants

consumer_key= constants.CONSUMER_KEY
consumer_secret= constants.CONSUMER_SECRET
access_token= constants.ACCESS_TOKEN
access_token_secret= constants.ACCESS_TOKEN_SECRET

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)
# These are the accounts for which you will fetch data
# It's a list of lists, with a category added for each handle
handles_list = ['aoc', 'BernieSanders', 'SenSchumer', 'ewarren','LeaderMcConnell', 'SenGillibrand']

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
    print ('Fetching @' + handle)
    try:
        user = api.get_user(handle)
        followers = user.followers_count
        description = user.description
        print (description)
        #insert_db(handle, category[0], followers, description)
    except:
        print ('-- ' + handle + ' not found')