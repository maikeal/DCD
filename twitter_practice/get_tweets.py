import os
import tweepy as tw
import pandas as pd
from datetime import datetime, timedelta

consumer_key= 'Rtb3TFQMq3XU21Ts9iomu8gjR'
consumer_secret= '9yaD24wAyOKnuEc8NNmu54mSrdrI53RMRDdDAGiMXoBvtZSeL3'
access_token= '1401632059752435717-JaYiSkecEZPcRpDvypY3QuM6pnQp5C'
access_token_secret= 'RzcsWDO23CaGGHeOGupEPBHhQj8pgE6f8pGCRsbZdZGiU'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

def get_tweets_since_yesterday():

	search_words = input("Search: ") + " -filter:retweets"
	date_since = (datetime.now() - timedelta(1)).strftime('%Y-%m-%d')

	tweets = tw.Cursor(api.search, q=search_words, lang="en", since=date_since).items(5)

	#print([tweet.text for tweet in tweets])

	tweets_and_user_info = [[tweet.text, tweet.user.screen_name, tweet.user.location, tweet.user.description] for tweet in tweets]
	#print(users_loc_and_bio)

	for t in tweets_and_user_info:
		print(t, "\n")

	get_tweets_since_yesterday()

get_tweets_since_yesterday()