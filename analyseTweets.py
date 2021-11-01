from demoji import replace_with_desc
import re
import spacy

# some things that need to be done once 
nlp = spacy.load("de_core_news_md")
mention = re.compile(r"@\w*")
link = re.compile(r"https?://[\w\.-/]*")


def containsKeyword(tweet: str, keyword: str, sim_single: float=0.7, sim_double: float=0.55) -> bool:
    """
    Process Tweet and tell wheter or not it contains a certain 
    keyword based an similarity of the word vectors. If it contains
    two words with a similarity over sim_double % (default: 70) or one word with a similarity 
    over sim_single % (default: 55) it returns True.
    """

    # replace some stuff in the tweet
    tweet = mention.sub(" ", tweet)
    tweet = link.sub(" ", tweet)
    tweet = tweet.replace('#', '')
    tweet = tweet.replace('\n', '')
    tweet = replace_with_desc(tweet)

    # use spaCy pipeline on tweet & kw to get vectors
    doc = nlp(tweet)
    tokens = [w for w in doc if not (w.is_punct or w.is_stop) and w.has_vector]
    kw_vector = nlp(keyword)

    # if keyword can't be vectorized, raise an Exception
    if not kw_vector.has_vector:
        raise KeyError('Keyword %s could not be vectorized', keyword)

    similarities = [kw_vector.similarity(w) for w in tokens]

    if max(similarities) >= 0.7:
        return True

    # count elements
    # bigger_double_sim = sum(s > sim_double for s in similarities)
    if sum(s > sim_double for s in similarities) > 2:
        return True

    # Otherwise
    return False