from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.by import By
from transformers import BlipProcessor, BlipForConditionalGeneration
from smolagents import tool, ToolCallingAgent

@tool
def click(driver: webdriver.Chrome, x: int, y: int) -> None:
    """
    This tool clicks on a specified absolute coordinate on the web page.
    Args:
        driver: The web driver instance.
        x: The x-coordinate to click.
        y: The y-coordinate to click.
    """
    action = ActionChains(driver)
    action.move_by_offset(x, y).click().perform()

@tool
def drag(driver: webdriver.Chrome, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
    """
    This tool drags from a specified start coordinate to an end coordinate.
    Args:
        driver: The web driver instance.
        start_x: The starting x-coordinate.
        start_y: The starting y-coordinate.
        end_x: The ending x-coordinate.
        end_y: The ending y-coordinate.
    """
    action = ActionChains(driver)
    action.move_by_offset(start_x, start_y).click_and_hold().move_by_offset(end_x - start_x, end_y - start_y).release().perform()

@tool
def get_screenshot(driver: webdriver.Chrome) -> bytes:
    """
    This tool captures the current screenshot of the web page.
    Args:
        driver: The web driver instance.
    Returns:
        A bytes object containing the screenshot.
    """
    return driver.get_screenshot_as_png()

@tool
def find_accept_button(screenshot: bytes) -> (int, int):
    """
    This tool finds the coordinates of the 'Accept' button in the screenshot.
    Args:
        screenshot: The screenshot of the web page.
    Returns:
        A tuple containing the x and y coordinates of the 'Accept' button.
    """
    # Implement image processing to locate the 'Accept' button
    # This can be done using template matching, OCR, or other techniques
    # For simplicity, let's assume we have a function `locate_button` that does this
    return locate_button(screenshot, "Accept")  # You need to implement this function


class CaptchaSolvingAgent(ToolCallingAgent):
    def __init__(self, driver):
        self.driver = driver
        # TODO - what do these do?
        self.processor = BlipProcessor.from_pretrained("Salesforce/blip-image-captioning-base")
        model = BlipForConditionalGeneration.from_pretrained("Salesforce/blip-image-captioning-base")

        tools = [click, drag, get_screenshot]

        prompt = (
            "You are an agent responsible for solving CAPTCHAs and interacting with modal boxes on web pages. "
            "You have access to the following tools: "
            "{{tool_descriptions}} "
            "{{managed_agents_descriptions}} "
            "Analyze the screenshot provided and determine the necessary actions to solve the CAPTCHA or interact with modal boxes. "
            "First, use 'get_screenshot' to capture the current state of the CAPTCHA or modal box. "
            "Then, decide on the actions needed, such as 'click' or 'drag'. "
            "Use the tools available to perform these actions. "
            "Your goal is to solve the CAPTCHA or interact with the modal box and verify if they are no longer present on the page."
        )


        super().__init__(tools=tools, model=model, system_prompt=prompt)

    def is_task_solved(self, screenshot):
        inputs = self.processor(images=Image.open(BytesIO(screenshot)), return_tensors="pt")
        caption_ids = self.model.generate(**inputs)
        result = self.model.decode(caption_ids[0], skip_special_tokens=True)
        return "captcha solved" in result.lower()

