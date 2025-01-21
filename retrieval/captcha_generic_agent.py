from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from transformers import BlipProcessor, BlipForConditionalGeneration
from smolagents import tool, ToolCallingAgent

@tool
def click(driver, selector: str) -> None:
    """
    This tool clicks on a specified element on the web page.
    Args:
        driver: The web driver instance.
        selector: The CSS selector of the element to click.
    """
    # TODO - don't find by selector, find by coordinates
    element = driver.find_element(By.CSS_SELECTOR, selector)
    element.click()

@tool
def drag(driver, selector: str, offset_x: int) -> None:
    """
    This tool drags a specified element to a target position.
    Args:
        driver: The web driver instance.
        selector: The CSS selector of the element to drag.
        offset_x: The horizontal offset to drag the element.
    """
    # TODO - don't find by selector, find by coordinates
    element = driver.find_element(By.CSS_SELECTOR, selector)
    action = webdriver.common.action_chains.ActionChains(driver)
    action.click_and_hold(element).move_by_offset(offset_x, 0).release().perform()

@tool
def get_screenshot(driver) -> bytes:
    """
    This tool captures the current screenshot of the web page.
    Args:
        driver: The web driver instance.
    Returns:
        A bytes object containing the screenshot.
    """
    return driver.get_screenshot_as_png()


class CaptchaSolvingAgent(ToolCallingAgent):
    def __init__(self, driver):
        self.driver = driver
        # TODO - what do these do?
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        tools = [click, drag, get_screenshot]

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
        
        super().__init__(tools=tools, model=model, system_prompt=prompt)

    def is_task_solved(self, screenshot):
        inputs = self.processor(images=Image.open(BytesIO(screenshot)), return_tensors="pt")
        caption_ids = self.model.generate(**inputs)
        result = self.model.decode(caption_ids[0], skip_special_tokens=True)
        return "captcha solved" in result.lower()

