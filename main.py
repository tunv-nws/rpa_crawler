import os

from RPA.Browser.Selenium import Selenium
from crawler import Crawler
from dotenv import load_dotenv


browser_lib = Selenium()


# Define a main() function that calls the other functions in order:
def main():
    load_dotenv()
    url = os.getenv("URL")
    search_pharse = os.getenv("SEARCH_PHARSE") or ""
    if not url or not search_pharse:
        return None

    filter_section = os.getenv("FILTER_SECTION") or ""
    filter_type = os.getenv("FILTER_TYPE") or ""
    filter_period_option = os.getenv("FILTER_PERIOD_OPTION") or ""
    sort_option = os.getenv("SORT_OPTION") or ""
    crawler = Crawler(url)
    crawler.run(
        search_pharse,
        filter_section,
        filter_type,
        filter_period_option,
        sort_option,
    )


# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
