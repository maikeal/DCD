import twitter
import os
import tweepy as tw
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# Set the Twitter API authentication
api = twitter.Api(consumer_key='bkjbjkbdbbkdjjbebfebbdejkbdjebdjkbek',
                  consumer_secret='jbdjebjdebdfbeivfvevfevfvvfevjkvfevifvevfiejk',
                  access_token_key='jwdgwoidgwodudevdkejvbifkedvwldlwblkbkbkldb',
                  access_token_secret='jbdjebdbebdbefbdebfevfvebfeubfke,bfelkbflebeblje')

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
