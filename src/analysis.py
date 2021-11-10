from typing import Tuple
import tweepy
import pandas as pd
import os
import json
import logging
from dotenv import load_dotenv

from analyseTweets import containsKeyword
from db import DataBase

TWEET_DIRECTORY = '/home/conda/Projekte/Daten/MdB_Tweets'
MDBS_FILE = 'MdBs_twitter.csv'

def createDirectory(dirName):
    """
    Safe method to create directories and proceed if they already exist.
    """
    try:
        os.mkdir(dirName)
    except FileExistsError:
        pass


def initializeTwitter(env: str='/root/.env') -> tweepy.API:
    """
    Initialize the connection to the twitter API.
    """
    load_dotenv(env)
    auth = tweepy.OAuthHandler(os.getenv('twitter_api_key'), os.getenv('twitter_api_secret_key'))
    auth.set_access_token(os.getenv('twitter_access_token'), os.getenv('twitter_access_secret_token'))

    api = tweepy.API(auth)
    return api


def loadMdBs(file: str) -> pd.DataFrame:
    """
    Load a dataframe with name, party and twitter handle of the MdBs.
    """
    mdbs = pd.read_csv(file)

    # only those where the twitter id is known
    mdbs = mdbs[mdbs['Twitter_Id'] != 0]

    # remove / since this would be interpreted as subfolder in mkdir
    mdbs['Party'] = mdbs['Party'].replace('CDU/CSU', 'CDU_CSU')
    mdbs['Party'] = mdbs['Party'].replace('Bündnis 90/Die Grünen', 'Bündnis90_DieGrünen')

    return mdbs


def createPartyDirectories(path: str,  mdbs: pd.DataFrame):
    """
    If not existing, create a directory for a Party to store tweets in.
    """
    # mkdir to save tweets in
    createDirectory(path)

    # mkdirs for parties
    for party in mdbs['Party'].unique():
        createDirectory(os.path.join(path, party))


def createMdBDirectory(path: str,  mdb: pd.Series) -> str:
    """
    If not existing, create a directory for a MdB to store tweets in.
    """
    current_dir = os.path.join(TWEET_DIRECTORY, mdb['Party'], mdb['Name'].strip() + '_' + mdb['First_Name'].strip())
    createDirectory(current_dir)
    return current_dir


def getTweets(api: tweepy.API, current_dir: str, mdb: pd.Series) -> list:
    """
    Get the latest tweets from a MdB based on the dictionary 
    they are stored in.
    """
    # get id of latest tweet
    try:
        latest_tweet = max(os.listdir(current_dir))
    except ValueError:
        # ValueError occurs when no tweets are saved
        latest_tweet = None

    # get Tweets
    try:
        tweets = api.user_timeline(user_id=mdb['Twitter_Id'], since_id=latest_tweet, include_rts=False, tweet_mode='extended', count=30)
    except (tweepy.errors.Forbidden, tweepy.errors.Unauthorized):
        tweets = []
    except Exception as e:
        logging.error(e)

    return tweets


def analyseTweet(tweet, keyword_dict, total, party) -> dict: 
    """
    Process & analyse a tweet and store it afterwards.
    """
    information = {
        'id': tweet.id,
        'text': tweet.full_text,
        'date': tweet.created_at.date().isoformat(),
        'keywords': {
            # 'kw': True
        }
    }

    # create an ISO8601 string for the creation date
    # months = {
    #     'Jan': '01',
    #     'Feb': '02',
    #     'Mar': '03',
    #     'Apr': '04',
    #     'May': '05',
    #     'Jun': '06',
    #     'Jul': '07',
    #     'Aug': '08',
    #     'Sep': '09',
    #     'Oct': '10',
    #     'Nov': '11',
    #     'Dec': '12'
    #     }
    # d = tweet.created_at.split(' ')
    # try:
    #     information['date'] = d[-1] + '-' + months[d[1]] + '-' + d[2]
    # except KeyError:
    #     logging.error('No month found for ' + d[1])

    for kw in keyword_dict.keys():
        contains = containsKeyword(information['text'], kw)
        information['keywords'][kw] = contains
        keyword_dict[kw][party].append(information['date'])

    total[party].append(information['date'])

    return information


def saveTweet(tweet_info: dict, directory: str):
    """
    Save a tweet to a document.
    """
    with open(os.path.join(directory, str(tweet_info['id'])), 'w') as f:
        f.write(json.dumps(tweet_info))


def createkeywordDict(parties: list, kw_file: str) -> Tuple[dict, dict]:
    """
    Create dictionaries to store the results of an analysis temporarily in.
    """
    keywordDict = {}
    with open(kw_file) as file:
        keywords = file.read().split('\n')
    for keyword in keywords:
        keywordDict[keyword] = {}
        for party in parties:
            keywordDict[keyword][party] = []
    
    totals = {}
    for party in parties:
        totals[party] = []
    return keywordDict, totals

def saveResults(keywordDict, totals):
    """
    Open a connection to the database and save the results in there.
    """
    db = DataBase()
    db.createDB(totals.keys(), keywordDict.keys())
    db.saveTweets(keywordDict, totals)
    db.close()


if __name__=='__main__':
    api = initializeTwitter()
    mdbs = loadMdBs(MDBS_FILE)
    createPartyDirectories(TWEET_DIRECTORY, mdbs)
    keywordDict, totals = createkeywordDict(mdbs['Party'].unique(), 'keywords.txt')
    try:
        for idx, mdb in mdbs.iterrows():
            # create subdir for this mdb
            current_dir = createMdBDirectory(TWEET_DIRECTORY, mdb)
            tweets = getTweets(api, current_dir, mdb)

            # prepare counting of total tweets
            party = mdb['Party']

            # save tweets
            for tweet in tweets:
                details = analyseTweet(tweet, keywordDict, totals, party)
                saveTweet(details, current_dir)
            
            logging.info('Finished tweets of ' + mdb['Name'])
    finally:
        # save the results
        saveResults(keywordDict, totals)
