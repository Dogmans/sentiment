import tweepy
from sentiment_analysis import SentimentAnalysis

class TwitterSentiment(SentimentAnalysis):
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        super().__init__()
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def fetch_data(self, query, count=100):
        tweets = self.api.search_tweets(q=query, count=count)
        return [tweet.text for tweet in tweets]
