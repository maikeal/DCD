import os
import tweepy 
import tweepy
import pandas as pd
import sqlite3
from datetime import datetime, timedelta

# Authentication details. To  obtain these visit dev.twitter.com
# The consumer keys can be found on your application's Details
# page located at https://dev.twitter.com/apps (under "OAuth settings")
consumer_key= 'eTwR2lbd6dMxCq988wtWnBvGC'
consumer_secret= 'IEsaSATulZcZyBE6QWxzK97dBU12wB7ORbVBk7kqUrYZNTfOxM'

# The access tokens can be found on your applications's Details
# page located at https://dev.twitter.com/apps (located 
# under "Your access token")
access_token= '1404645710058987522-2tHLCZnMazsLg86yBKL3s5ZUrHX6hB'
access_token_secret= 'B1YbGzAFbRrAOhLS1867uJIVza30v4GLifQIOb7gA04Cm'



if __name__ == '__main__':
    user = input ("Please enter the twitter user handle you want collect:") # selct user id

    # Create authentication token
    auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
    auth.set_access_token(access_token, access_token_secret)

    api = tweepy.API(auth)
    
    print ("Getting statistics for", user)

    # Get information about the user
    data = api.get_user(user)
    
    print ('Followers: ' + str(data.followers_count))
    print ('Tweets: ' + str(data.statuses_count))
    print ('Favouries: ' + str(data.favourites_count))
    print ('Friends: ' + str(data.friends_count))
    print ('Appears on ' + str(data.listed_count) + ' lists')