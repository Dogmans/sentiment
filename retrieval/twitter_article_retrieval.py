import tweepy
import os
from .article_retrieval import ArticleRetrieval

class TwitterArticleRetrieval(ArticleRetrieval):
    def __init__(self):
        super().__init__()
        # Get credentials from environment variables
        api_key = os.getenv('TWITTER_API_KEY')
        api_secret = os.getenv('TWITTER_API_SECRET')
        access_token = os.getenv('TWITTER_ACCESS_TOKEN')
        access_token_secret = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

        # Validate credentials
        if not all([api_key, api_secret, access_token, access_token_secret]):
            raise ValueError("Missing Twitter API credentials. Please set the TWITTER_API_KEY, "
                           "TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, and "
                           "TWITTER_ACCESS_TOKEN_SECRET environment variables.")

        # Initialize Twitter API
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def fetch_data(self, stock_data, count=100):
        # Search using both symbol and company name for better results
        query = f"{stock_data.symbol} OR {stock_data.company_name}"
        tweets = self.api.search_tweets(q=query, count=count)
        return [tweet.text for tweet in tweets]
