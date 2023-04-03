from lxml import html
import requests
from bs4 import BeautifulSoup

webpage = requests.get("https://www.indymedia.nl/node/53148")
soup = BeautifulSoup(webpage.content, 'html.parser')

allowlist = ['p']
test_text = [text for text in soup.find_all(text = True) if text.parent.name in allowlist]
test_string = ''.join(test_text)

