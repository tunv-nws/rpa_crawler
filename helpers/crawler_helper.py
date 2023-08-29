from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By


def get_element(
    web_element: WebElement,
    element: str,
    type: str = By.CSS_SELECTOR,
) -> WebElement:
    return web_element.find_element(type, element)


def get_multi_elements(
    web_element: WebElement,
    element: str,
    type: str = By.CSS_SELECTOR,
) -> list[WebElement]:
    return web_element.find_elements(type, element)
