import twitter
import os
import tweepy as tw
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# Set the Twitter API authentication
api = twitter.Api(consumer_key='eTwR2lbd6dMxCq988wtWnBvGC',
                  consumer_secret='IEsaSATulZcZyBE6QWxzK97dBU12wB7ORbVBk7kqUrYZNTfOxM',
                  access_token_key='1404645710058987522-2tHLCZnMazsLg86yBKL3s5ZUrHX6hB',
                  access_token_secret='B1YbGzAFbRrAOhLS1867uJIVza30v4GLifQIOb7gA04Cm')

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