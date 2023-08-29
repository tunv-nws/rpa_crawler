import os
import re
import logging

from RPA.Browser.Selenium import Selenium
from SeleniumLibrary.errors import ElementNotFound
from selenium.common.exceptions import (
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.by import By
from typing import Optional, Tuple

from urllib.parse import urlparse
from helpers.excel_helper import ExcelHelper

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime
from utils.date_utils import get_months_ago, convert_datetime_to_string
from utils.file_utils import check_directory_exist

logger = logging.getLogger(__name__)

SEARCH_RESULT_XPATH = "//*[@id='site-content']/div/div[2]/div[1]/ol"


def to_int(value: str) -> Optional[int]:
    """Convert string to integer."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


class Crawler:
    """Crawler executions."""

    def __init__(self, website: str) -> None:
        self.crawler = Selenium()
        self.website = website
        self.excel_helper = ExcelHelper("Crawl_data.xlsx")

    def run(
        self,
        search_pharse: str,
        filter_section: str,
        filter_type: str,
        filter_period_option: int,
    ) -> None:
        try:
            self._prepare()
            news_list = self._do_search(
                search_pharse,
                filter_section,
                filter_type,
                filter_period_option,
            )

            excel_data = []
            for news in news_list:
                try:
                    news_data = self._extract_news_data(news, search_pharse)
                    excel_data.append(news_data)
                except Exception as e:
                    logger.exception(str(e))
                    continue

            self.excel_helper.write(excel_data)

        finally:
            self.crawler.close_all_browsers()

    def _prepare(self) -> None:
        self._open_the_website()
        self._press_the_continue_with_policy_button()

    def _do_search(
        self,
        search_pharse: str,
        filter_section: str,
        filter_type: str,
        filter_period_option: int,
    ) -> None:
        self._enter_search_pharse(search_pharse)

        self._select_search_section(filter_section)
        self._select_search_type(filter_type)
        self._enter_search_period(filter_period_option)

        self._show_all_search_result()
        return self._get_news_list()

    def _wait_until_return_search_result(self):
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.XPATH, SEARCH_RESULT_XPATH))
        )

    def _click_search_sign(self) -> None:
        """Click the search button for showing up the search input."""

    def _enter_search_pharse(self, pharse: str) -> None:
        # click the button search first
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.XPATH,
                    "//*[@id='app']/div[2]/div[2]/header/section[1]/div[1]/div[2]/button",
                )
            )
        ).click()
        input_field = "//*[@id='search-input']/form/div/input"
        self.crawler.input_text(input_field, pharse)
        self.crawler.press_keys(input_field, "ENTER")
        self._wait_until_return_search_result()

    def _select_search_section(self, choosen_section: str) -> None:
        section_elems = self._get_section_elements()
        for elem in section_elems:
            # section is a span tag and inside of it, it has another span tag
            # the sub span tag represent for total article
            section = elem.find_element(By.TAG_NAME, "span")
            if choosen_section in section.text:
                section.click()
                self._wait_until_return_search_result()

    def _get_section_elements(self) -> list:
        form = self.driver.find_element(
            By.XPATH, "//*[@id='site-content']/div/div[1]/div[2]/div/div/div[2]/div/div"
        )
        dropdown_button_elem = form.find_element(
            By.CSS_SELECTOR,
            "button[data-testid*='search-multiselect-button']",
        )
        dropdown_button_elem.click()
        sections = form.find_element(
            By.CSS_SELECTOR,
            "ul[data-testid*='multi-select-dropdown-list']",
        )
        return sections.find_elements(By.TAG_NAME, "li")

    def _select_search_type(self, choosen_type: str) -> None:
        if not choosen_type:
            return

        type_elems = self._get_type_elements()
        for elem in type_elems:
            # type is a span tag and inside of it, it has another span tag
            # the sub span tag represent for total article
            type = elem.find_element(By.TAG_NAME, "span")
            if choosen_type in type.text:
                type.click()
                self._wait_until_return_search_result()

    def _get_type_elements(self) -> list:
        """Get list of types."""
        form = self.driver.find_element(
            By.XPATH, "//*[@id='site-content']/div/div[1]/div[2]/div/div/div[3]/div/div"
        )
        dropdown_button_elem = form.find_element(
            By.CSS_SELECTOR,
            "button[data-testid*='search-multiselect-button']",
        )
        dropdown_button_elem.click()
        sections = form.find_element(
            By.CSS_SELECTOR,
            "ul[data-testid*='multi-select-dropdown-list']",
        )
        return sections.find_elements(By.TAG_NAME, "li")

    def _enter_search_period(self, filter_option: int) -> None:
        start_date, end_date = self._get_search_period(filter_option)
        form = self.driver.find_element(
            By.XPATH,
            "//*[@id='site-content']/div/div[1]/div[2]/div/div/div[1]/div/div",
        )
        dropdown_button_elem = form.find_element(
            By.CSS_SELECTOR,
            "button[data-testid*='search-date-dropdown-a']",
        )
        dropdown_button_elem.click()
        self._click_specific_date_option(form)

        start_date_input = form.find_element(
            By.CSS_SELECTOR,
            "input[data-testid*='DateRange-startDate']",
        )
        if start_date:
            start_date_input.send_keys(start_date)

        end_date_input = form.find_element(
            By.CSS_SELECTOR,
            "input[data-testid*='DateRange-endDate']",
        )
        end_date_input.send_keys(end_date)
        self._wait_until_return_search_result()

    def _click_specific_date_option(self, form: WebElement) -> None:
        option = form.find_elements(By.TAG_NAME, "li")[-1]
        option.click()

    def _get_search_period(self, filter_option: int) -> Tuple[str, str]:
        filter_option = to_int(filter_option)
        if filter_option is None:
            return None, None

        date_format = "%m/%d/%Y"
        end_date = datetime.now()
        months_ago = filter_option - 1
        if months_ago >= 1:
            start_date = get_months_ago(end_date, months=months_ago)
            start_date = convert_datetime_to_string(start_date, format=date_format)
        else:
            start_date = None

        end_date = convert_datetime_to_string(end_date, format=date_format)
        return start_date, end_date

    def _show_all_search_result(self) -> None:
        try:
            show_more_button = self.driver.find_element(
                By.XPATH, "//*[@id='site-content']/div/div[2]/div[2]/div/button"
            )
            while self.crawler.is_element_visible(show_more_button):
                show_more_button.click()
        except (ElementNotFound, StaleElementReferenceException):
            return None

    def _open_the_website(self) -> None:
        self.crawler.open_available_browser(self.website, maximized=True)
        self.driver = self.crawler.driver

    def _press_the_continue_with_policy_button(self):
        try:
            button_ele = '//*[@id="complianceOverlay"]/div/button'
            button = self.crawler.find_element(button_ele)
            button.click()
        except ElementNotFound:
            return

    def _get_news_list(self) -> list:
        """Get all the news from the search's result."""
        search_result = self.driver.find_element(By.XPATH, SEARCH_RESULT_XPATH)
        news = search_result.find_elements(
            By.CSS_SELECTOR,
            "li[data-testid*='search-bodega-result']",
        )
        return news

    def _extract_news_data(self, news: WebElement, search_pharse: str) -> None:
        date = self._extract_text_by_tag_name(news, "span")
        image_name, image_path = self._save_image(news)

        content = news.find_element(By.TAG_NAME, "a")
        title = self._extract_text_by_tag_name(content, "h4")
        description = self._extract_text_by_tag_name(content, "p")

        total_search_pharse_appear = self._count_search_pharse_appear_in_news(
            search_pharse,
            title,
            description,
        )
        return {
            "title": title,
            "date": date,
            "description": description,
            "search_pharse_appear": total_search_pharse_appear,
            "image_name": image_name,
            "image_path": image_path,
            "exist_moneys": self._is_money_exist_in_title_or_description(
                title, description
            ),
        }

    def _extract_text_by_tag_name(self, news: WebElement, tag_name: str) -> str:
        try:
            elem = news.find_element(By.TAG_NAME, tag_name)
            return elem.text
        except StaleElementReferenceException:
            return ""

    def _save_image(self, news: WebElement) -> Optional[str]:
        """Save image to computer and return the file path."""
        try:
            image = news.find_element(By.TAG_NAME, "img")
            image_name = self._extract_image_name(image.get_attribute("src"))
            static_path = os.path.join("images")
            check_directory_exist(static_path)
            image_path = os.path.join(static_path, image_name)
            with open(image_path, "wb") as file:
                file.write(image.screenshot_as_png)
            return image_name, image_path

        except (NoSuchElementException, StaleElementReferenceException):
            return None, None

    def _extract_image_name(self, src: str) -> str:
        parse = urlparse(src)
        return os.path.basename(parse.path)

    def _count_the_text_appear(
        self,
        search_pharse: str,
        text: str,
    ) -> int:
        matches = re.findall(search_pharse, text, re.IGNORECASE)
        return len(matches) if matches else 0

    def _count_search_pharse_appear_in_news(
        self,
        search_pharse: str,
        title: str,
        description: str,
    ) -> int:
        total_appear_in_title = self._count_the_text_appear(search_pharse, title)
        total_appear_in_description = self._count_the_text_appear(
            search_pharse,
            description,
        )
        return total_appear_in_title + total_appear_in_description

    def _is_money_exist_in_title_or_description(
        self,
        title: str,
        description: str,
    ) -> bool:
        expressions = [
            r"(^\$(\d+))",
            r"(^\$(?:\d*\.\d{1,2}))",
            r"(\d* (?:USD|dollars))",
            r"(^\$(?:\d{3},)?(?:\d{3},)*\d{3}\.\d+)",
        ]
        pattern = "|".join(expressions)
        if re.search(pattern, title) or re.search(pattern, description):
            return True
        else:
            return False
