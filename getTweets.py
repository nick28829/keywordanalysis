import twitter
import pandas as pd
import os
from dotenv import load_dotenv

TWEET_DIRECTORY = '/home/conda/Projekte/Daten/MdB_Tweets'

def createDirectory(dirName):
    # safe method to create directories and proceed if they already exist
    try:
        os.mkdir(dirName)
    except FileExistsError:
        pass


if __name__=='__main__':
    load_dotenv('/root/.env')
    api = twitter.Api(
        consumer_key=os.getenv('twitter_api_key'),
        consumer_secret=os.getenv('twitter_api_secret_key'),
        access_token_key=os.getenv('twitter_access_token'),
        access_token_secret=os.getenv('twitter_access_secret_token')
    )

    mdbs = pd.read_csv('MdBs_twitter.csv')

    # only those where the twitter id is known
    mdbs = mdbs[mdbs['Twitter_Id'] != 0]

    # remove / since this would be interpreted as subfolder in mkdir
    mdbs['Party'] = mdbs['Party'].replace('CDU/CSU', 'CDU_CSU')
    mdbs['Party'] = mdbs['Party'].replace('Bündnis 90/Die Grünen', 'Bündnis90_DieGrünen')


    # mkdir to save tweets in
    createDirectory(TWEET_DIRECTORY)

    # mkdirs for parties
    for party in mdbs['Party'].unique():
        createDirectory(os.path.join(TWEET_DIRECTORY, party))

    for idx, mdb in mdbs.iterrows():
        
        # create subdir for this mdb
        current_dir = os.path.join(TWEET_DIRECTORY, mdb['Party'], mdb['Name'] + '_' + mdb['First_Name'])
        createDirectory(current_dir)

        # get id of latest tweet
        try:
            latest_tweet = max(os.listdir(current_dir))
        except ValueError:
            # ValueError occurs when no tweets are saved
            latest_tweet = None

        # get Tweets
        try:
            tweets = api.GetUserTimeline(user_id=mdb['Twitter_Id'], since_id=latest_tweet)
        except twitter.error.TwitterError:
            pass


        # save tweets
        for tweet in tweets:
            with open(os.path.join(current_dir, str(tweet.id)), 'w') as file:
                # save the date of creation in the files
                d = tweet.created_at.split(' ')
                date = d[2] + '.' + d[1] + ' ' + d[-1]
                content =  date + ' ::: ' + tweet.text
                file.write(content)
