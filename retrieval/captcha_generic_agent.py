from PIL import Image
from io import BytesIO
from selenium import webdriver
from transformers import GPT4VForConditionalGeneration
from smolagents import tool, ToolCallingAgent


@tool
def click(driver: webdriver.Chrome, x: int, y: int) -> None:
    action = ActionChains(driver)
    action.move_by_offset(x, y).click().perform()

@tool
def drag(driver: webdriver.Chrome, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
    action = ActionChains(driver)
    action.move_by_offset(start_x, start_y).click_and_hold().move_by_offset(end_x - start_x, end_y - start_y).release().perform()

@tool
def get_screenshot(driver: webdriver.Chrome) -> bytes:
    return driver.get_screenshot_as_png()


class CaptchaSolvingAgent(ToolCallingAgent):
    def __init__(self, driver):
        self.driver = driver
        self.model = GPT4VForConditionalGeneration.from_pretrained("openai/gpt-4v")

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

        super().__init__(tools=tools, model=self.model, system_prompt=prompt)

    def is_task_solved(self, screenshot):
        inputs = self.model(images=Image.open(BytesIO(screenshot)), return_tensors="pt")
        caption_ids = self.model.generate(**inputs)
        result = self.model.decode(caption_ids[0], skip_special_tokens=True)
        return "captcha solved" in result.lower()
