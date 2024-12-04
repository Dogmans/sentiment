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
    def __init__(self):
        super().__init__()
        self.base_url = None
        self.search_url_template = None
        self.article_link_filter = None

    def fetch_article_content(self, url):
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        paragraphs = soup.find_all('p')
        article_text = ' '.join([para.get_text() for para in paragraphs])
        return article_text

    def fetch_data(self, query, count=10):
        if not all([self.base_url, self.search_url_template, self.article_link_filter]):
            raise NotImplementedError("Child class must set base_url, search_url_template, and article_link_filter")

        search_url = self.search_url_template.format(query=query)
        print("fetching data from", search_url)
        response = requests.get(search_url)
        soup = BeautifulSoup(response.content, 'html.parser')

        articles = []
        for link in soup.find_all('a', href=True):
            if self.article_link_filter(link['href']):
                article_url = self.get_full_article_url(link['href'])
                article_text = self.fetch_article_content(article_url)
                articles.append(article_text)
                if len(articles) >= count:
                    break
        return articles

    def get_full_article_url(self, href):
        if href.startswith('http'):
            return href
        return self.base_url + href

class MotleyFoolSentiment(WebScrapingSentiment):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.fool.com'
        self.search_url_template = '{base_url}/search/?q={query}'.format(base_url=self.base_url, query='{query}')
        self.article_link_filter = lambda href: '/investing/' in href

class MsnMoneySentiment(WebScrapingSentiment):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://www.msn.com'
        self.search_url_template = 'https://www.msn.com/en-us/search?q={query}+site:money.msn.com'
        self.article_link_filter = lambda href: 'money.msn.com' in href

class YahooFinanceSentiment(WebScrapingSentiment):
    def __init__(self):
        super().__init__()
        self.base_url = 'https://finance.yahoo.com'
        self.search_url_template = '{base_url}/quote/{query}/news?p={query}'.format(base_url=self.base_url, query='{query}')
        self.article_link_filter = lambda href: href.startswith('/news/')

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
