import re
import time
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import nltk
from nltk.tokenize import sent_tokenize
import torch
from transformers import pipeline, BlipForConditionalGeneration, BlipProcessor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

nltk.download('punkt', quiet=True)

class ArticleRetrieval:

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def __init__(self, requests_per_second=10):
        self.relevance_pipeline = pipeline(
            "zero-shot-classification",
            model="facebook/bart-large-mnli",
            device=0 if torch.cuda.is_available() else -1
        )
        self.blip_processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.blip_model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
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
        page_source = self.driver.page_source
        self.last_request_time = time.time()
        
        if self._detect_captcha(page_source):
            self._solve_captcha()
            page_source = self.driver.page_source
        
        self._url_cache[url] = page_source
        return page_source

    def _detect_captcha(self, page_source):
        soup = BeautifulSoup(page_source, 'html.parser')
        return bool(soup.find('div', class_='g-recaptcha') or soup.find('iframe', title='recaptcha challenge'))

    def _solve_captcha(self):
        try:
            captcha_iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="recaptcha challenge"]'))
            )
            self.driver.switch_to.frame(captcha_iframe)

            # Detect the CAPTCHA prompt text
            captcha_prompt = self.driver.find_element(By.CSS_SELECTOR, 'div[class*="prompt"]').text

            # Capture all the image elements
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img.captcha-image')

            images = []
            for img_element in image_elements:
                img_src = img_element.get_attribute('src')
                self.driver.get(img_src)
                captcha_image = Image.open(BytesIO(self.driver.page_source))
                images.append((img_element, captcha_image))

            # Process and classify the images based on the CAPTCHA prompt
            for img_element, img in images:
                inputs = self.blip_processor(images=img, return_tensors="pt")
                caption = self.blip_model.generate(**inputs)
                solution_text = self.blip_processor.decode(caption[0], skip_special_tokens=True)

                # Check if the solution text matches the prompt (e.g., "bus", "bicycle", etc.)
                if any(word in solution_text.lower() for word in captcha_prompt.lower().split()):
                    img_element.click()

            self.driver.switch_to.default_content()
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        except Exception as e:
            print(f"Error solving CAPTCHA: {str(e)}")

    def chunk_text(self, text):
        sentences = sent_tokenize(text)
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
        text = re.sub(r'[^\w\s]', ' ', text)
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

            hypothesis_template = "This text is about {}."
            labels = [
                f"{info.shortName} ({info.symbol})",
                "unrelated company or topic"
            ]
            
            relevant_chunks = []
            for chunk in chunks:
                result = self.relevance_pipeline(
                    chunk,
                    labels,
                    hypothesis_template=hypothesis_template,
                    multi_label=False
                )
                
                if result['labels'][0] == labels[0] and result['scores'][0] > 0.7:
                    relevant_chunks.append(chunk)
            
            return relevant_chunks
            
        except Exception as e:
            print(f"Error checking relevance: {str(e)}")
            return []

    def fetch_data(self, data):
        raise NotImplementedError("Subclasses must implement fetch_data")
