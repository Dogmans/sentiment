import praw
from sentiment_analysis import SentimentAnalysis

class RedditSentiment(SentimentAnalysis):
    def __init__(self, client_id, client_secret, user_agent):
        super().__init__()
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def fetch_data(self, query, count=100):
        submissions = self.reddit.subreddit(query).new(limit=count)
        return [submission.title + ' ' + submission.selftext for submission in submissions if submission.selftext]
