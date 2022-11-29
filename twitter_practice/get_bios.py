import os
import tweepy as tw
import pandas as pd
from datetime import datetime, timedelta

consumer_key= 'aa5xPHnUlFIVJrMb0QuCSAMFk'
consumer_secret= 'CsatdSlbLXm4bUiJLKa4ZpDYBxkNEpdYq2zZL3jlaRf1U5VmyF'
access_token= '1401632059752435717-msitAGNwn4n9Q8ddVk4V0E4eFhVrve'
access_token_secret= 'StkY7ZMvFF21UYRjc1kXbOBtCans0xuBR53Frw4fGx9DM'

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