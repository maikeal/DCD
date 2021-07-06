import twitter
import os
import tweepy as tw
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

import constants
consumer_key= constants.CONSUMER_KEY
consumer_secret= constants.CONSUMER_SECRET
access_token= constants.ACCESS_TOKEN
access_token_secret= constants.ACCESS_TOKEN_SECRET

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

# set a handle
handle = 'aoc'

# Get some info on a user
user = api.GetUser(screen_name=handle)

print user.GetName()
print user.GetDescription()
print user.GetFollowersCount()
print user.GetStatusesCount()
print user.GetUrl()

# get a user timeline
statuses = api.GetUserTimeline(screen_name='pokjournal', count=1)
print [s.text for s in statuses]