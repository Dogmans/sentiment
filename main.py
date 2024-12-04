# main.py
import os
from sentiment_analysis import TwitterSentiment, RedditSentiment, MotleyFoolSentiment, MsnMoneySentiment, YahooFinanceSentiment

# Define Twitter API credentials
TWITTER_API_KEY = os.getenv('TWITTER_API_KEY')
TWITTER_API_SECRET = os.getenv('TWITTER_API_SECRET')
TWITTER_ACCESS_TOKEN = os.getenv('TWITTER_ACCESS_TOKEN')
TWITTER_ACCESS_TOKEN_SECRET = os.getenv('TWITTER_ACCESS_TOKEN_SECRET')

# Define Reddit API credentials
REDDIT_CLIENT_ID = os.getenv('REDDIT_CLIENT_ID')
REDDIT_CLIENT_SECRET = os.getenv('REDDIT_CLIENT_SECRET')
REDDIT_USER_AGENT = os.getenv('REDDIT_USER_AGENT')

def main():
    # List of sentiment analysis classes
    # sentiment_classes = [
    #     TwitterSentiment(
    #         TWITTER_API_KEY, TWITTER_API_SECRET, TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET
    #     ),
    #     RedditSentiment(
    #         REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
    #     ),
    #     MotleyFoolSentiment(),
    #     MsnMoneySentiment(),
    #     YahooFinanceSentiment()
    # ]

    sentiment_classes = [
        MotleyFoolSentiment(),
        MsnMoneySentiment(),
        YahooFinanceSentiment()
    ]

    # Define the queries
    queries = ['AAPL', 'TSLA', 'GOOGL']

    # Iterate over the sentiment analysis classes and fetch & analyze data for each query
    for sentiment_class in sentiment_classes:
        for query in queries:
            results = sentiment_class.fetch_and_analyze(query)
            platform = sentiment_class.__class__.__name__.replace('Sentiment', '')
            print(f"{platform} Sentiment Analysis for '{query}':")
            for text, sentiment in results:
                print(f"Text: {text}\nSentiment: {sentiment}\n")

if __name__ == "__main__":
    main()
