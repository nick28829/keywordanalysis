# Political Keyword Analysis
## Intention
The idea behind this project is to analyse which poltical party does tweet about which topic how often. Therefore, I analyse the the twitter feed of all MdBs I found the twitter handle for.
## Getting a list of all MdBs
Since I did not find a CSV-file with all MdBs, I had to create one myself. Therefore, I crawled the official site of the Bundestag 
(https://www.bundestag.de/abgeordnete). I used the code found in crawl_mdbs.py and got the file MDBs.csv. 
## Finding their twitter accounts
A bit more complicated was finding the twitter accounts for the mdbs. I used the twitter API to search for the name. Additionally, I added another term: Either mdb, Bundestag or the name of the corresponding party. If all three searches did not return results, the id is set to 0.     
During this step, I had a small problem: the twitter API does only allow a certain amount of requests per 15 minute time period. If doing more requests, an exception is raised. To deal with this, I added an counter counting the requests. If more than 800 requests are made, the script paueses for 15 minutes and resumes afterwards. If an exception occurs, the current state should be saved to resume afterwards (which did not happen so I did not have to build a script that can resume at a later point).
## Getting and saving past tweets

### Structure Data
Party/Politician-Name/Date/tweetid

### Saving the data
To save:
- Party
- Day
- Word 
- Mentions 


## Updating the tweets

## Preparing the words to search for


## Analizing the tweets
Vectorize the words with https://devmount.github.io/GermanWordEmbeddings/
- word2vec auf Tweets/Parteiprogrammen trainieren

### Pipeline
- 0. Normalization
- 1. Remove Stopwords
- 2. Lemmatization
- 3. Convert words to vectors
- 4. Compare vector of keyword with vectors of other words

## Building the API

## Building the GUI

## Deployment