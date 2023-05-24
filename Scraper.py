from lxml import html
import requests
from bs4 import BeautifulSoup
import re


def scrape_it_mate(url: str, date_time_text_search: str = None, date_time_class_search: list = None, allowlist: list = None):
    '''
    Outputs a list containing [text of article, datetime of posting, url]


    :param url: Input url
    :param date_time_text_search: Optional, the datetime text to search for in case the datetime is not in <time> element
    :param date_time_class_search: Optional, the datetime class to search for in case the date is in some class. has to be a list [tag, class]
    :param allowlist: html elements allowed to search in for text
    :return:
    '''

    # Default allowlist
    if allowlist is None:
        allowlist = ['p', 'span']

    # Get webpage and make soup
    webpage = requests.get(url)
    soup = BeautifulSoup(webpage.content, 'html.parser')

    # Get the text of the soup
    text = [text for text in soup.find_all(text=True) if text.parent.name in allowlist]
    string = ''.join(text)

    # Either use a string input to search for datetime information or find the <time> html element
    if date_time_text_search is not None:
        date_time = [date for date in soup(text=re.compile(date_time_text_search))]

    elif date_time_class_search is not None:
        date_time = [date_time for date_time in soup.find_all(date_time_class_search[0], class_=date_time_class_search[1])]

    else:
        date_time = [date_time for date_time in soup.find_all('time')]

    scraped_data = [string, date_time, url]

    return scraped_data


test_result = scrape_it_mate("https://www.ninefornews.nl/world-economic-forum-kondigt-zomer-davos-aan-en-hier-vindt-de-bijeenkomst-plaats/", date_time_class_search=['span', 'date meta-item tie-icon'])
test_result_2 = scrape_it_mate('https://gedachtenvoer.nl/2023/04/08/hoe-krijg-jij-je-leven-weer-op-de-rit/')
# TODO: Write scraping function. -> Done
# TODO: Save scraped text + url somewhere -> Done
# TODO: Find way to have the scraper filter on class tags ST article comments can be ignored (or scraped seperately)
