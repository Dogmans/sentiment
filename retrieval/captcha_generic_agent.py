from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from transformers import BlipProcessor, BlipForConditionalGeneration
from smolagents import ToolCallingAgent
from webdriver_manager.chrome import ChromeDriverManager

class ClickTool:
    def __init__(self, driver):
        self.driver = driver

    def click(self, selector):
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        element.click()

class DragTool:
    def __init__(self, driver):
        self.driver = driver

    def drag(self, selector, offset_x):
        element = self.driver.find_element(By.CSS_SELECTOR, selector)
        action = webdriver.common.action_chains.ActionChains(self.driver)
        action.click_and_hold(element).move_by_offset(offset_x, 0).release().perform()


class CaptchaSolvingAgent(ToolCallingAgent):
    def __init__(self, driver):
        self.driver = driver
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        tools = {
            "click": ClickTool(driver).click,
            "drag": DragTool(driver).drag,
            "get_screenshot": self.get_screenshot
        }
        
        prompt = (
            "You are an agent responsible for solving CAPTCHAs on web pages. "
            "You have access to the following tools: "
            "- 'get_screenshot': Captures the current screenshot of the web page. "
            "- 'click': Clicks on a specified element on the web page. "
            "- 'drag': Drags a specified element to a target position. "
            "Analyze the screenshot provided and determine the necessary actions to solve the CAPTCHA. "
            "First, use 'get_screenshot' to capture the current state of the CAPTCHA. "
            "Then, decide on the actions needed to solve the CAPTCHA, such as 'click' or 'drag'. "
            "Use the tools available to perform these actions. "
            "Your goal is to solve the CAPTCHA and verify if the CAPTCHA is no longer present on the page."
        )
        
        super().__init__(tools=tools, model=model, processor=self.processor, prompt=prompt)

    def get_screenshot(self):
        return self.driver.get_screenshot_as_png()

    def is_task_solved(self, screenshot):
        inputs = self.processor(images=Image.open(BytesIO(screenshot)), return_tensors="pt")
        caption_ids = self.model.generate(**inputs)
        result = self.processor.decode(caption_ids[0], skip_special_tokens=True)
        return "captcha solved" in result.lower()

