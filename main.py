from RPA.Browser.Selenium import Selenium
from crawler import Crawler

browser_lib = Selenium()


# Define a main() function that calls the other functions in order:
def main():
    url = "https://www.nytimes.com/"
    search_pharse = "iniesta"
    filter_section = "Blogs"
    filter_type = ""
    filter_period_option = 0
    crawler = Crawler(url)
    crawler.run(
        search_pharse,
        filter_section,
        filter_type,
        filter_period_option,
    )

# Call the main() function, checking that we are running as a stand-alone script:
if __name__ == "__main__":
    main()
