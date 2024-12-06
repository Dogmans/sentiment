# sentiment_analysis.py
import tweepy
import praw
import requests
from bs4 import BeautifulSoup
from transformers import pipeline

class SentimentAnalysis:
    def __init__(self):
        self.sentiment_model = pipeline('sentiment-analysis', model='distilbert-base-uncased-finetuned-sst-2-english')

    def fetch_and_analyze(self, query, count=100):
        data = self.fetch_data(query, count)
        sentiments = []
        for text in data:
            analysis = self.sentiment_model(text)
            sentiments.append((text, analysis[0]))
        return sentiments

    def fetch_data(self, query, count):
        raise NotImplementedError("Subclasses should implement this method")

class WebScrapingSentiment(SentimentAnalysis):
    def __init__(self, domain):
        super().__init__()
        self.search_url_template = 'https://www.bing.com/search?q={query}:site={domain}&freshness=Day'
        self.domain = domain

    def article_link_filter(self, query, link_text):
        # Use the LLM to check if the link text is relevant to the stock query
        prompt = f"Is this headline relevant to {query} stock: {link_text}"
        try:
            analysis = self.sentiment_model(prompt)
            return analysis[0]['label'] == 'POSITIVE'
        except Exception as e:
            print(f"Error analyzing link relevance: {e}")
            # Fall back to basic keyword matching if LLM fails
            relevant_terms = ['stock', 'market', 'invest', query.lower()]
            return any(term in link_text.lower() for term in relevant_terms)

    def fetch_data(self, query, count=10):
        search_url = self.search_url_template.format(query=query, domain=self.domain)
        print("fetching data from", search_url)
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []
        for result in soup.find_all('li', class_='b_algo'):
            link = result.find('a', href=True)
            link_text = link.get_text() if link else ""
            if link and self.article_link_filter(query, link_text):
                article_text = self.fetch_article_content(link['href'])
                articles.append(article_text)
                if len(articles) >= count:
                    break
        return articles

    def fetch_article_content(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join([para.get_text() for para in paragraphs])
        return article_text

class TwitterSentiment(SentimentAnalysis):
    def __init__(self, api_key, api_secret, access_token, access_token_secret):
        super().__init__()
        auth = tweepy.OAuthHandler(api_key, api_secret)
        auth.set_access_token(access_token, access_token_secret)
        self.api = tweepy.API(auth)

    def fetch_data(self, query, count=100):
        tweets = self.api.search_tweets(q=query, count=count)
        return [tweet.text for tweet in tweets]

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
