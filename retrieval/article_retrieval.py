import time
from PIL import Image
from io import BytesIO
from bs4 import BeautifulSoup
import nltk
import torch
from transformers import pipeline, BlipForConditionalGeneration, BlipProcessor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from image_slider_captcha import ImageSliderCaptcha
from image_grid_captcha import ImageGridCaptcha


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

    def _capture_screenshot(self, element):
        # Capture a screenshot of the specified element
        return element.screenshot_as_png

    def _detect_captcha_type_image(self, image):
        # Use an image recognition model to determine the CAPTCHA type based on the screenshot
        inputs = self.blip_processor(images=Image.open(BytesIO(image)), return_tensors="pt")
        caption = self.blip_model.generate(**inputs)
        solution_text = self.blip_processor.decode(caption[0], skip_special_tokens=True)

        if "grid" in solution_text.lower():
            return 'grid'
        elif "slider" in solution_text.lower():
            return 'slider'
        return None

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
        # Capture a screenshot of the entire page
        screenshot = self.driver.get_screenshot_as_png()
        
        # Determine CAPTCHA type using the screenshot
        captcha_type = self._detect_captcha_type_image(screenshot)
        
        # Choose the appropriate solver based on CAPTCHA type
        if captcha_type == 'grid':
            solver = ImageGridCaptcha(self.driver, self.blip_processor, self.blip_model)
        elif captcha_type == 'slider':
            solver = ImageSliderCaptcha(self.driver, self.blip_processor, self.blip_model)
        solver.solve()

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

            hypothesis_template = "This text is relevant to "
            labels = ["relevant", "not relevant"]

            result = self.relevance_pipeline(
                text,
                labels,
                hypothesis_template=hypothesis_template,
                multi_label=False
            )

            return result['labels'][0] == "relevant" and result['scores'][0] > 0.7

        except Exception as e:
            print(f"Error determining relevance: {str(e)}")
            return False