# -*- coding: utf-8 -*-
"""
@author: Steven Marin
Simple twitter scraper.
Given a list of user names, it gets information such as name, followers, friends,
nuber of tweets, description, location and user urls if any.
It also scrapes all the tweets for the given accounts with their respective 
number of likes and retweets.
Stores all this data into an excel file .xlsx. One tab for the general info of
the users and one tab for each user containing all of their tweets.
"""

import pandas as pd
import configparser
import tweepy

""" List of usernames to scrape"""
USERS = ['cnnbrk','bbcmundo', 'dw_espanol', 'BBCBreaking', 'TheRealNews', 
         'guardiannews', 'Reuters', 'TheOnion','FRANCE24', 'CNN', 'ABC', 
         'MSNBC', 'NBCNews', 'CBSNews']





""" Function that configures the twitter api"""
def config_api():
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
    return api


api = config_api()



user_list = []
tweets_list = []
for user in USERS:
    user_info = api.get_user(screen_name=user)
    user_dict = {'name':user_info.name, 'screen_name':user_info.screen_name,
                 'followers': user_info.followers_count, 'friends':user_info.friends_count, 
                 'tweets':user_info.statuses_count,
                 'user_description' : user_info.description, 'location':user_info.location,
                 'user_urls':user_info.entities['url']['urls'][0]['expanded_url']}
    user_list.append(user_dict)


    tweets = api.user_timeline(screen_name=user, count=200,include_rts = False,
                               tweet_mode = 'extended')
    all_tweets = []
    all_tweets.extend(tweets)
    oldest_id = tweets[-1].id
    while True:
        tweets = api.user_timeline(screen_name=user, count=200,
                                   include_rts = False, max_id = oldest_id - 1,
                                   tweet_mode = 'extended')
        if len(tweets) == 0:
            break
        oldest_id = tweets[-1].id
        all_tweets.extend(tweets)
        print('N of tweets downloaded until now {}'.format(len(all_tweets)))
    
    
    outtweets = [[tweet.id_str, 
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





