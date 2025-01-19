from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from transformers import BlipProcessor, BlipForConditionalGeneration
from smolagents import Agent
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

class CaptchaSolvingAgent(Agent):
    def __init__(self, driver):
        super().__init__()
        self.driver = driver
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        self.model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")
        self.click_tool = ClickTool(self.driver)
        self.drag_tool = DragTool(self.driver)
        self.prompt = (
            "You are an agent responsible for solving CAPTCHAs on web pages. "
            "You have access to tools for clicking and dragging elements on the page. "
            "Analyze the screenshot provided and determine the necessary actions to solve the CAPTCHA. "
            "Use the tools available to perform these actions. If you recognize a slider, drag it to the correct position. "
            "If you recognize images to click, click on the appropriate ones. "
            "Your goal is to solve the CAPTCHA and verify if the CAPTCHA is no longer present on the page."
        )

    def available_tools(self):
        return {
            "click": self.click_tool.click,
            "drag": self.drag_tool.drag
        }

    def decide_action(self, screenshot):
        # Include the prompt in the analysis
        inputs = self.processor(images=Image.open(BytesIO(screenshot)), return_tensors="pt")
        caption = self.model.generate(**inputs, prompt=self.prompt)
        action = self.processor.decode(caption[0], skip_special_tokens=True)
        return action

    def is_captcha_solved(self, screenshot):
        # Analyze the screenshot to determine if the CAPTCHA is gone
        inputs = self.processor(images=Image.open(BytesIO(screenshot)), return_tensors="pt")
        caption = self.model.generate(**inputs)
        result = self.processor.decode(caption[0], skip_special_tokens=True)
        return "captcha solved" in result.lower()

    def solve_captcha(self):
        while True:
            screenshot = self.driver.get_screenshot_as_png()
            if self.is_captcha_solved(screenshot):
                break
            action = self.decide_action(screenshot)
            tool, selector, value = self.parse_action(action)
            self.available_tools()[tool](selector, value)
            time.sleep(2)  # Give some time for the action to take effect  

    def parse_action(self, action):
        # Parse the action string to extract tool, selector, and value
        parts = action.split()
        tool = parts[0]
        selector = parts[2].strip("'")
        value = int(parts[-1]) if tool == "drag" else None
        return tool, selector, value

# Example usage
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
agent = CaptchaSolvingAgent(driver)
agent.solve_captcha()
