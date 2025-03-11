import time
from bs4 import BeautifulSoup
import nltk
import torch
from transformers import pipeline
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from .captcha_generic_agent import CaptchaSolvingAgent


nltk.download('punkt', quiet=True)


class ArticleRetrieval:

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def __init__(self, requests_per_second=10):
        self.relevance_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        self.max_length = 512
        self.delay = 1.0 / requests_per_second if requests_per_second > 0 else 0
        self.last_request_time = 0
        self._url_cache = {}

    def _is_article_page(self, page_source):
        try:
            soup = BeautifulSoup(page_source, 'html.parser')
            text = ' '.join([p.get_text() for p in soup.find_all('p')])

            if len(text.split()) < 50:
                return False

            hypothesis_template = "This text is an article."
            labels = ["article", "non-article"]

            result = self.relevance_pipeline(
                text,
                labels,
                hypothesis_template=hypothesis_template,
                multi_label=False
            )

            return result['labels'][0] == "article" and result['scores'][0] > 0.7

        except Exception as e:
            print(f"Error determining article status: {str(e)}")
            return False

    def _rate_limited_request(self, url):
        if url in self._url_cache:
            return self._url_cache[url]

        now = time.time()
        time_since_last = now - self.last_request_time
        
        if time_since_last < self.delay:
            time.sleep(self.delay - time_since_last)
        
        self.driver.get(url)
        self.last_request_time = time.time()
        self._solve_captcha()
        page_source = self.driver.page_source
        
        self._url_cache[url] = page_source
        return page_source

    def _solve_captcha(self):
        # Choose the appropriate solver based on CAPTCHA type
        captcha_solver = CaptchaSolvingAgent(self.driver)
        captcha_solver.run()

    def chunk_text(self, text):
        sentences = nltk.sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence.split())
            
            if current_length + sentence_length <= self.max_length:
                current_chunk.append(sentence)
                current_length += sentence_length
            else:
                if current_chunk:
                    chunks.append(' '.join(current_chunk))
                current_chunk = [sentence]
                current_length = sentence_length
        
        if current_chunk:
            chunks.append(' '.join(current_chunk))
            
        return chunks

    def _preprocess_text(self, text: str) -> str:
        text = ' '.join(text.split())
        return text.lower()

    def get_link_relevant_chunks(self, link, info):
        try:
            page_source = self._rate_limited_request(link)
            article_soup = BeautifulSoup(page_source, 'html.parser')
            paragraphs = article_soup.find_all('p')
            article_text = ' '.join([p.get_text() for p in paragraphs])
            
            if article_text:
                return self.extract_relevant_chunks(article_text, info)
                    
        except Exception as e:
            print(f"Error fetching article from {link}: {str(e)}")
            
        return []

    def extract_relevant_chunks(self, text, info):
        try:
            text = self._preprocess_text(text)
            chunks = self.chunk_text(text)
            if not chunks:
                return []

            hypothesis_template = "This text is relevant to {label}"
            labels = [info['symbol'], info['shortName']]

            result = self.relevance_pipeline(
                text,
                labels,
                hypothesis_template=hypothesis_template,
                multi_label=False
            )

            return result['labels'][0] in labels and result['scores'][0] > 0.7

        except Exception as e:
            print(f"Error determining relevance: {str(e)}")
            return False