import praw
import os
from article_retrieval import ArticleRetrieval

class RedditArticleRetrieval(ArticleRetrieval):
    def __init__(self):
        super().__init__()
        # Get credentials from environment variables
        client_id = os.getenv('REDDIT_CLIENT_ID')
        client_secret = os.getenv('REDDIT_CLIENT_SECRET')
        user_agent = os.getenv('REDDIT_USER_AGENT')

        # Validate credentials
        if not all([client_id, client_secret, user_agent]):
            raise ValueError("Missing Reddit API credentials. Please set the REDDIT_CLIENT_ID, "
                           "REDDIT_CLIENT_SECRET, and REDDIT_USER_AGENT environment variables.")

        # Initialize Reddit API
        self.reddit = praw.Reddit(
            client_id=client_id,
            client_secret=client_secret,
            user_agent=user_agent
        )

    def fetch_data(self, query, count=100):
        submissions = self.reddit.subreddit(query).new(limit=count)
        return [submission.title + ' ' + submission.selftext for submission in submissions if submission.selftext]
