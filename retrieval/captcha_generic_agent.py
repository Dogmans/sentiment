# TODO - make more sophisticated
# https://huggingface.co/docs/smolagents/en/examples/multiagents


from PIL import Image
from io import BytesIO
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
from transformers import BLIP2ForConditionalGeneration
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
        self.model = BLIP2ForConditionalGeneration.from_pretrained("Salesforce/blip2")

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
            "Your goal is to solve the CAPTCHA or interact with the modal box and verify if they are no longer present on the page. "
            "Return 'true' if the CAPTCHA is solved, and 'false' if it is not."
        )

        super().__init__(tools=tools, model=self.model, system_prompt=prompt)


# Example usage
if __name__ == "__main__":
    driver = webdriver.Chrome()  # Initialize the web driver
    driver.get("https://www.marketwatch.com")  # Navigate to MarketWatch website
    agent = CaptchaSolvingAgent(driver)

    # Run the agent to solve the CAPTCHA
    is_solved = agent.run()
    print("CAPTCHA solved:", is_solved)
