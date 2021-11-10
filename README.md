# Political Keyword Analysis
## Intention
The idea behind this project is to analyse which poltical party does tweet about which topic how often. Therefore, I analyse the the twitter feed of all MdBs I found the twitter handle for.

## What I've done
If you are interested in finding out what I've done in more detail, you can read the medium article I wrote. It is not yet published, but you can find the draft [here](https://medium.com/@nicklas_bocksberger/analysing-keywords-tweeted-by-politicians-779a7139ca81)

## Components
### MdB Crawler
The script in `crawl_mdbs.py` crawls https://www.bundestag.de/abgeordnete to create a list with all MdBs.

### Finding their twitter accounts
In `findPoliticiansOnTwitter` I search for the Twitter IDs for the MdBs.

### Analysing tweets
The analysis consists of the following steps:
- 0. Normalization
- 1. Remove Stopwords
- 2. Lemmatization
- 3. Convert words to vectors
- 4. Compare vector of keyword with vectors of other words     

In `analysis.py`, I stream the tweets, apply the analysis and afterwards store the tweets.

### Storing Data
For storing the results, I use a SQLite database, defined in `db.py`.

### API/GUI
The server utilizing aiohttp can be found in `api.py`, the served HTML in `home.html`.

### Keyowrds
In `keywords.txt` you can find the list I search in tweets for.