# -*- coding: utf-8 -*-
"""
Created on Tue Mar 22 00:14:08 2022

@author: Steven Marin
"""

import pandas as pd
import configparser
import tweepy
from time import sleep

# read config
config = configparser.ConfigParser()
config.read('config.ini')

api_key = config['twitter']['api_key']
api_key_secret = config['twitter']['api_key_secret']

access_token = config['twitter']['access_token']
access_token_secret = config['twitter']['access_token_secret']

# authenticate
auth = tweepy.OAuthHandler(api_key, api_key_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth)


#get general info on the list of accounts
users_of_interest = ['cnnbrk','bbcmundo', 'dw_espanol', 'BBCBreaking',
                     'TheRealNews', 'guardiannews', 'Reuters', 'TheOnion',
                     'FRANCE24', 'CNN', 'ABC', 'MSNBC', 'NBCNews', 'CBSNews']
user_list = []
tweets_list = []
for user in users_of_interest:
    user_info = api.get_user(screen_name=user)
    user_dict = {'name':user_info.name, 'screen_name':user_info.screen_name,
                 'followers': user_info.followers_count, 'friends':user_info.friends_count, 
                 'tweets':user_info.statuses_count,
                 'user_description' : user_info.description, 'location':user_info.location,
                 'user_urls':user_info.entities['url']['urls'][0]['expanded_url']}
    user_list.append(user_dict)

    
    #getting all tweets
    # userID = users_of_interest[1] 
    
    
    tweets = api.user_timeline(screen_name=user, 
                               # 200 is the maximum allowed count
                               count=200,
                               include_rts = False,
                               # Necessary to keep full_text 
                               # otherwise only the first 140 words are extracted
                               tweet_mode = 'extended'
                               )
    
    
    all_tweets = []
    all_tweets.extend(tweets)
    oldest_id = tweets[-1].id
    while True:
        # sleep(1)
        tweets = api.user_timeline(screen_name=user, 
                               # 200 is the maximum allowed count
                               count=200,
                               include_rts = False,
                               max_id = oldest_id - 1,
                               # Necessary to keep full_text 
                               # otherwise only the first 140 words are extracted
                               tweet_mode = 'extended'
                               )
        if len(tweets) == 0:
            break
        oldest_id = tweets[-1].id
        all_tweets.extend(tweets)
        print('N of tweets downloaded till now {}'.format(len(all_tweets)))
    
    
    outtweets = [[tweet.id_str, 
                  #tweet.created_at, 
                  tweet.favorite_count, 
                  tweet.retweet_count, 
                  tweet.full_text.encode("utf-8").decode("utf-8")] 
                 for idx,tweet in enumerate(all_tweets)]
    
    tweets_dict = {'user':user, 'tweets':outtweets}
    tweets_list.append(tweets_dict)




df_user = pd.DataFrame(user_list)

""" Writing the final excel spreadsheet with ..."""
with pd.ExcelWriter('output.xlsx') as writer:  
    df_user.to_excel(writer, sheet_name='Users', index = False)
    for each in tweets_list:
        user = each['user']
        tweets = each['tweets']
        df_tweets = pd.DataFrame(tweets,columns=["id","favorite_count","retweet_count", "text"])
        df_tweets.to_excel(writer,sheet_name = user, index=False)






#getting all tweets
userID = users_of_interest[1] 


tweets = api.user_timeline(screen_name=userID, 
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )


all_tweets = []
all_tweets.extend(tweets)
oldest_id = tweets[-1].id
while True:
    # sleep(1)
    tweets = api.user_timeline(screen_name=userID, 
                           # 200 is the maximum allowed count
                           count=200,
                           include_rts = False,
                           max_id = oldest_id - 1,
                           # Necessary to keep full_text 
                           # otherwise only the first 140 words are extracted
                           tweet_mode = 'extended'
                           )
    if len(tweets) == 0:
        break
    oldest_id = tweets[-1].id
    all_tweets.extend(tweets)
    print('N of tweets downloaded till now {}'.format(len(all_tweets)))


outtweets = [[tweet.id_str, 
              tweet.created_at, 
              tweet.favorite_count, 
              tweet.retweet_count, 
              tweet.full_text.encode("utf-8").decode("utf-8")] 
             for idx,tweet in enumerate(all_tweets)]
df = pd.DataFrame(outtweets,columns=["id","created_at","favorite_count","retweet_count", "text"])











public_tweets = api.home_timeline()


columns = ['Time', 'User', 'Tweet']

data = []
for tweet in public_tweets:
    data.append([tweet.created_at, tweet.user.screen_name, tweet.text])

df = pd.DataFrame(data, columns=columns)


tweets = api.user_timeline(id='BBCWorld', count=200)
tweets_extended = api.user_timeline(id='BBCWorld', tweet_mode='extended', count=200)
 
# Print number of tweets
print(len(tweets))


to_extract = [
    'id',
    'created_at',
    'text',
    'full_text',
    'retweeted',
    'favorited',
    'is_quote_status',
    'retweet_count',
    'favorite_count',
    'lang',
    'in_reply_to_status_id',
    'in_reply_to_user_id'
    ]
 
tweet_entities = [
    ('hashtags','text'),
    ('user_mentions','screen_name'),
    ('urls','expanded_url')
]
tweets_data = []
 
for tweet in tweets_extended:
    tweet = tweet._json
    tweet_data = {}
    for e in to_extract:
        try:
            tweet_data[e]=tweet[e]
        except:
            continue
    for entity in tweet_entities:
        entity_list = []
        for t in tweet['entities'][entity[0]]:
            entity_list.append(t[entity[1]])
        tweet_data[entity[0]] = entity_list
 
    tweets_data.append(tweet_data)
    # Get Tweet data
df = pd.DataFrame(tweets_data)