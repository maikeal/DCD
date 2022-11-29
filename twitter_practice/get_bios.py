import os
import tweepy as tw
import pandas as pd
from datetime import datetime, timedelta

consumer_key= 'Consumer_key'
consumer_secret= 'Consumer_secret'
access_token= 'Access_token'
access_token_secret= 'Acess_token_secret'

auth = tw.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tw.API(auth, wait_on_rate_limit=True)

def get_bio():
	handle = input("Handle: @")
	try :
		bio = api.get_user(handle).description
		print(bio)
	except tw.error.TweepError:
		print("User {} not found".format(handle))
	get_bio()

get_bio()
