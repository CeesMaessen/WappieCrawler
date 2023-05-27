from lxml import html
import requests
from bs4 import BeautifulSoup
import re

def extract_urls_from_single_string(url_string: str) -> list:
    '''
    Turns one big string of urls seperated by '; ' into a list of urls.
    the '; ' seperator is a result from concatenating lines in PyCharm with ctrl+shift+j

    :param url_string: string of urls
    :return: list of urls
    '''
    urls = list(url_string.split('; '))
    return urls

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

    htmls = [html['href'] for html in soup.find_all('a', href=True)]

    return htmls


test_result = scrape_it_mate("https://www.transitieweb.nl/", date_time_class_search=['span', 'published'])
test_result_2 = scrape_it_mate("https://www.transitieweb.nl/", date_time_class_search=['span', 'date meta-item tie-icon'])



