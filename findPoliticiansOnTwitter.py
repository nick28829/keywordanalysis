import pandas as pd
import twitter
import time
import pickle
import os


if __name__=='__main__':
    api = twitter.Api(
        consumer_key=os.getenv('twitter_api_key'),
        consumer_secret=os.getenv('twitter_api_secret_key'),
        access_token_key=os.getenv('twitter_access_token'),
        access_token_secret=os.getenv('twitter_access_secret_token')
    )

    mdbs = pd.read_csv('MdBs.csv')
    ids = []

    requests = 0
    try:
        for idx, politician in mdbs.iterrows():
            if requests > 800:
                time.sleep(900)
                requests = 0
            search_name = '{0} {1} mdb'.format(politician['First_Name'], politician['Name'], politician['Party'])
            qs = api.GetUsersSearch(search_name, count=1)
            requests += 1
            if len(qs) > 0:
                id = qs[0].id
            else:
                search_name = '{0} {1} {2}'.format(politician['First_Name'], politician['Name'], politician['Party'])
                qs = api.GetUsersSearch(search_name, count=1)
                requests += 1
                if len(qs) > 0:
                    id = qs[0].id
                else:
                    search_name = '{0} {1} Bundestag'.format(politician['First_Name'], politician['Name'], politician['Party'])
                    qs = api.GetUsersSearch(search_name, count=1)
                    requests += 1
                    if len(qs) > 0:
                        id = qs[0].id
                    else:
                        id = 0
            ids.append(id)            

        mdbs['Twitter_Id'] = ids
        mdbs.to_csv('MdBs_twitter.csv')
    except:
        with open('twitterids.pickle', 'wb') as f:
            pickle.dump(ids, f)
