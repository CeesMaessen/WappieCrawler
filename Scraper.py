from lxml import html
import requests
from bs4 import BeautifulSoup


def scrape_it_mate(url):
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, 'html.parser')
    allowlist = ['p']
    test_text = [text for text in soup.find_all(text = True) if text.parent.name in allowlist]
    test_string = ''.join(test_text)

    scraped_data = [test_string, url]

    return scraped_data

scrape_it_mate("https://www.indymedia.nl/node/53163")
# TODO: Write scraping function. -> Done
# TODO: Save scraped text + url somewhere -> Done
# TODO: Find way to have the scraper filter on class tags ST article comments can be ignored (or scraped seperately)