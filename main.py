import time
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import pandas as pd
import requests
from Scraper import scrape_it_mate


class WappieCrawler:

    # Make lists to see which websites have been visited and which ones are in queue.
    def __init__(self, website_queue, root_domain, wait_time=2, max_visits=100):
        self.visited_websites = []
        self.urls_to_scrape = []
        self.website_queue = website_queue
        self.wait_time = wait_time
        self.max_visits = max_visits
        self.root_domain = root_domain

   # Use Beautiful soup to download html and find a hrefs
    def soup_download_html_and_get_hrefs(self, url):
        # Make Soup
        webpage = requests.get(url)
        soup = BeautifulSoup(webpage.content, 'html.parser')

        # Dont DDoS
        time.sleep(self.wait_time)

        # Find all hrefs in soup
        hrefs = [href['href'] for href in soup.find_all('a', href=True)]

        # If the href starts with / we have to add the root domain to it
        for i, href in enumerate(hrefs):
            if href.startswith('/'):
                hrefs[i] = urljoin(url, href)

        return hrefs

    def add_new_url_to_queue(self, url):
        if url not in self.visited_websites and url not in self.website_queue:

            # Only save hrefs in the scrape list if root domain is correct and it is not a pdf
            if url.startswith(self.root_domain) and not url.endswith('pdf'):
                self.website_queue.append(url)
                self.urls_to_scrape.append(url)  # Add the URL to the list of URLs to scrape.

    def crawl(self, url):
        # Start crawling
        hrefs = self.soup_download_html_and_get_hrefs(url)
        for href in hrefs:
            self.add_new_url_to_queue(href)

    def go(self):
        while self.website_queue and len(self.visited_websites) <= self.max_visits:
            url = self.website_queue.pop(0)
            print(f'Current scrape list size: {len(self.urls_to_scrape)} for domain {self.root_domain}.')

            try:
                self.crawl(url)

            except Exception:
                print(f'Failed to crawl {url}')
            self.visited_websites.append(url)

        print(f'Found these urls to scrape {self.urls_to_scrape}')


def scrape_df_and_csv(crawler_obj: WappieCrawler, csv_name: str, allowlist: list = None,
                      date_time_text_search: str = None, date_time_class_search: list = None):
    '''
    Scrapes urls given a WappieCrawler object by looking at its urls_to_scrape list. Returns a df and saves a csv of this df.
    Will search for <time> elements if no text or class search is provided.

    :param crawler_obj: The crawler object
    :param csv_name: The name of the csv. Needs to be 'xxxxx.csv'
    :param allowlist: Optional list of allowed html elements to scrape for text
    :param date_time_class_search: date_time_class_search: Optional, the datetime class to search for in case the date is in some class. has to be a list [tag, class]
    :param date_time_text_search: Optional, the datetime text to search for in case the datetime is not in <time> element

    :return: dataframe with columns [text, date, url]
    '''
    results = []

    # scrape all urls in the list of urls to scrape
    for url in crawler_obj.urls_to_scrape:
        # Have to make sure we are only scraping urls from the root domain

        try:
            print(f"Now scraping: {url}")
            # Searching for the date time in the text with a specific string
            results.append(scrape_it_mate(url, allowlist=allowlist, date_time_text_search=date_time_text_search,
                                              date_time_class_search=date_time_class_search))
        except:
            print(f'Failed to scrape {url}')

    # save results to csv file
    results_df = pd.DataFrame(results, columns=['text', 'date', 'url'])
    results_df.to_csv(csv_name, index=False)

    return results_df


if __name__ == '__main__':
    # create a crawler object containing all urls of domain indymedia.nl
    indy_media_crawler = WappieCrawler(website_queue=['https://www.indymedia.nl/'], root_domain='https://www.indymedia.nl/', wait_time=1, max_visits=40)
    indy_media_crawler.go()
    # Scrape date based on text search
    indy_media_df = scrape_df_and_csv(indy_media_crawler, csv_name='results_indymedia.csv', date_time_text_search='gepost door:')

    niburu_crawler = WappieCrawler(website_queue=['https://niburu.co/'], root_domain='https://niburu.co/', wait_time=1, max_visits=40)
    niburu_crawler.go()
    # Scrape date based on time element
    niburu_df = scrape_df_and_csv(niburu_crawler, csv_name='results_niburu.csv')

    nine_for_news_crawler = WappieCrawler(website_queue=['https://www.ninefornews.nl/'], root_domain='https://www.ninefornews.nl', wait_time=1, max_visits=40)
    nine_for_news_crawler.go()
    # Scrape date based on class search
    nine_for_news_df = scrape_df_and_csv(nine_for_news_crawler, csv_name='results_nine_for_news.csv', date_time_class_search=['span', 'date meta-item tie-icon'])

    # transitieweb_crawler = WappieCrawler(website_queue=['https://www.transitieweb.nl/'], root_domain='https://www.transitieweb.nl', wait_time=1, max_visits=20)
    # transitieweb_crawler.go()
    # # Scrape based on class search
    # transitieweb_df = scrape_df_and_csv(transitieweb_crawler, root_domain='https://www.transitieweb.nl', csv_name='results_transitieweb.csv', date_time_class_search=['span', 'published'])

    frontnieuws_crawler = WappieCrawler(website_queue=['https://www.frontnieuws.com/'], root_domain='https://www.frontnieuws.com', wait_time=1, max_visits=40)
    frontnieuws_crawler.go()
    # Scrape date based on time element
    frontnieuws_df = scrape_df_and_csv(frontnieuws_crawler, csv_name='results_frontnieuws.csv')

    # de_andere_krant_crawler = WappieCrawler(website_queue=['https://deanderekrant.nl'], root_domain='https://deanderekrant.nl', wait_time=1, max_visits=20)




# Example websites for in queue:
#     niburu.co
#     ninefornews.nl
#     hoezithetnuecht.nl
#     gedachtenvoer.nl can't be crawled (YET?)
#     transitieweb.nl
#     privacynieuws.nl concerned with privacy issues only, not realy extremist
#     frontnieuws.com
#     geenstijl.nl (100% complottheorie-vrij)
#     jensen.nl
#     indigorevolution.nl, wanttoknow.nl, martinvrijland.nl, ellaster.nl en finalwakeupcall.info (niet vaak geüpdatet)
# deanderekrant.nl
# ongehoordnederland.tv(?)

