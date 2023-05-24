import time
from urllib.parse import urljoin

import pandas as pd
import requests
from lxml import html

from Scraper import scrape_it_mate


class WappieCrawler:

    # Make lists to see which websites have been visited and which ones are in queue.
    def __init__(self, website_queue, wait_time=2, max_visits=100):
        self.visited_websites = []
        self.urls_to_scrape = []
        self.website_queue = website_queue
        self.wait_time = wait_time
        self.max_visits = max_visits

    # Download a webpage and return it as html file
    def download_html(self, url):
        webpage = requests.get(url)
        webpage_html = html.fromstring(webpage.text)
        time.sleep(self.wait_time)
        return webpage_html

    # Use lxml library to retrieve hrefs(links) from html files and form new links: url/{link}
    def get_href_from_html(self, url, webpage_html):
        for link in webpage_html.xpath('//a/@href'):
            if link.startswith('/'):
                # urljoin automatically slices {url}.
                # e.g. https://www.indymedia.nl/node/53163 becomes https://www.indymedia.nl.
                # Therefore urljoin doesnt produce https://www.indymedia.nl/node/53163/node/53168 for example.
                new_page = urljoin(url, link)
                print(f'Page found:{new_page}')
                yield new_page

    def add_new_url_to_queue(self, url):
        if url not in self.visited_websites and url not in self.website_queue:
            print(f'{url} added to queue')
            self.website_queue.append(url)
            self.urls_to_scrape.append(url)  # Add the URL to the list of URLs to scrape.

    def crawl(self, url):
        webpage_html = self.download_html(url)
        for new_page in self.get_href_from_html(url, webpage_html):
            self.add_new_url_to_queue(new_page)

    def go(self):
        while self.website_queue and len(self.visited_websites) <= self.max_visits:
            url = self.website_queue.pop(0)
            print('Current queue size: ', len(self.website_queue))
            print('Visited websites:', self.visited_websites)
            try:
                self.crawl(url)
            except Exception:
                print(f'Failed to crawl {url}')
            self.visited_websites.append(url)


def scrape_df_and_csv(crawler_obj: WappieCrawler, csv_name: str, allowlist: list = None, date_time_text_search: str = None, date_time_class_search: list = None):
    '''
    Scrapes urls given a WappieCrawler object by looking at its urls_to_scrape list. Returns a df and saves a csv of this df.
    Will search for <time> elements if no text or class search is provided.

    :param crawler_obj: The crawler object
    :param csv_name: The name of the csv. Needs to be 'xxxxx.csv'
    :param allowlist: Optional list of allowed html elements to scrape for text
    :param date_time_class_search: date_time_class_search: Optional, the datetime class to search for in case the date is in some class. has to be a list [tag, class]
    :param date_time_text_search: Optional, the datetime text to search for in case the datetime is not in <time> element
    :return:
    '''
    results = []

    # scrape all urls in the list of urls to scrape
    for url in crawler_obj.urls_to_scrape:
        print(f"Now scraping: {url}")
        # Searching for the date time in the text with a specific string
        results.append(scrape_it_mate(url, allowlist=allowlist, date_time_text_search=date_time_text_search, date_time_class_search=date_time_class_search))

    # save results to csv file
    results_df = pd.DataFrame(results, columns=['text', 'date', 'url'])
    results_df.to_csv(csv_name, index=False)

    return results_df


if __name__ == '__main__':
    # create a crawler object containing all urls of domain indymedia.nl
    #indy_media_crawler = WappieCrawler(website_queue=['https://www.indymedia.nl/'], wait_time=1, max_visits=10)
    #indy_media_crawler.go()
    #indy_media_df = scrape_df_and_csv(indy_media_crawler, csv_name='results_indymedia.csv', date_time_text_search='gepost door:')

    #niburu_crawler = WappieCrawler(website_queue=['https://niburu.co/'], wait_time=1, max_visits=10)
    #niburu_crawler.go()
    #niburu_df = scrape_df_and_csv(niburu_crawler, csv_name='results_niburu.csv')

    # Gives you a random post every time. Not really usable
    #nine_for_news_crawler = WappieCrawler(website_queue=['https://www.ninefornews.nl'], wait_time=5, max_visits=100)
    #nine_for_news_crawler.go()
    #nine_for_news_df = scrape_df_and_csv(nine_for_news_crawler, csv_name='results_nine_for_news.csv', date_time_class_search=['span', 'date meta-item tie-icon'])

    # Gedachtenvoer doesn't crawl for some reason
    #gedachtenvoer_crawler = WappieCrawler(website_queue=['http://gedachtenvoer.nl/'], wait_time=1, max_visits=10)
    #gedachtenvoer_crawler.go()
    #gedachtenvoer_df = scrape_df_and_csv(gedachtenvoer_crawler, csv_name='results_gedachtenvoer.csv')

    privacy_nieuws_crawler = WappieCrawler(website_queue=['https://privacynieuws.nl/'], wait_time=2, max_visits=10)
    privacy_nieuws_crawler.go()
    privacy_nieuws_df = scrape_df_and_csv(privacy_nieuws_crawler, csv_name= 'results_privacynieuws.csv')

# TODO: Add delay time to scraper and possibly more ways to find day time
# Example websites for in queue:
#     niburu.co
#     ninefornews.nl HEEFT CRAWLER PROTECTION
#     hoezithetnuecht.nl
#     gedachtenvoer.nl KAN NIET GECRAWLED WORDEN (YET?)
#     transitieweb.nl
#     privacynieuws.nl
#     frontnieuws.com
#     geenstijl.nl (100% complottheorie-vrij)
#     jensen.nl
#     indigorevolution.nl, wanttoknow.nl, martinvrijland.nl, ellaster.nl en finalwakeupcall.info (niet vaak geüpdatet)
# deanderekrant.nl
# ongehoordnederland.tv(?)
