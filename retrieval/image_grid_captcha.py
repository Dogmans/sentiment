import time
from PIL import Image
from io import BytesIO
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

class ImageGridCaptcha:
    def __init__(self, driver, blip_processor, blip_model):
        self.driver = driver
        self.blip_processor = blip_processor
        self.blip_model = blip_model

    def solve(self):
        try:
            captcha_iframe = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, 'iframe[title="recaptcha challenge"]'))
            )
            self.driver.switch_to.frame(captcha_iframe)

            captcha_prompt = self.driver.find_element(By.CSS_SELECTOR, 'div[class*="prompt"]').text
            image_elements = self.driver.find_elements(By.CSS_SELECTOR, 'img.captcha-image')

            images = []
            for img_element in image_elements:
                img_src = img_element.get_attribute('src')
                self.driver.get(img_src)
                captcha_image = Image.open(BytesIO(self.driver.page_source))
                images.append((img_element, captcha_image))

            for img_element, img in images:
                inputs = self.blip_processor(images=img, return_tensors="pt")
                caption = self.blip_model.generate(**inputs)
                solution_text = self.blip_processor.decode(caption[0], skip_special_tokens=True)

                if any(word in solution_text.lower() for word in captcha_prompt.lower().split()):
                    img_element.click()

            self.driver.switch_to.default_content()
            self.driver.find_element(By.CSS_SELECTOR, 'button[type="submit"]').click()

        except Exception as e:
            print(f"Error solving CAPTCHA: {str(e)}")