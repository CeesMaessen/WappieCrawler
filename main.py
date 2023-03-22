from lxml import html
import requests
from urllib.parse import urljoin
import time

class WappieCrawler:

# Make lists to see which websites have been visited and which ones are in queue.
    def __init__(self, website_queue):
        self.visited_websites = []
        self.website_queue = website_queue


# Download a webpage and return it as html file
    def download_html(self, url):
        webpage = requests.get(url)
        webpage_html = html.fromstring(webpage.text)
        time.sleep(10)
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


    def crawl(self, url):
        webpage_html = self.download_html(url)
        for new_page in self.get_href_from_html(url, webpage_html):
            self.add_new_url_to_queue(new_page)



    def go(self):
        while self.website_queue:
            url = self.website_queue.pop(0)
            #print('website queue', self.website_queue)
            print('Current queue size: ', len(self.website_queue))
            print('Visited websites:', self.visited_websites)
            try:
                self.crawl(url)
            except Exception:
                print(f'Failed to crawl {url}')
            self.visited_websites.append(url)


if __name__ == '__main__':
    WappieCrawler(website_queue=['https://www.indymedia.nl/']).go()


# TODO: Save scraped html files. Find best way to save html files for using NLP algorithms.
# Example websites for in queue:
#     niburu.co
#     ninefornews.nl
#     hoezithetnuecht.nl
#     gedachtenvoer.nl
#     transitieweb.nl
#     privacynieuws.nl
#     frontnieuws.com
#     geenstijl.nl (100% complottheorie-vrij)
#     jensen.nl
#     indigorevolution.nl, wanttoknow.nl, martinvrijland.nl, ellaster.nl en finalwakeupcall.info (niet vaak geüpdatet)
# deanderekrant.nl
# ongehoordnederland.tv(?)