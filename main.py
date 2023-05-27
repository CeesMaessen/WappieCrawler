import time
from urllib.parse import urljoin

import pandas as pd
import requests
from lxml import html

from Scraper import scrape_it_mate, extract_urls_from_single_string


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
        print(f"Now scraping: {url}")
        # Searching for the date time in the text with a specific string
        results.append(scrape_it_mate(url, allowlist=allowlist, date_time_text_search=date_time_text_search,
                                      date_time_class_search=date_time_class_search))

    # save results to csv file
    results_df = pd.DataFrame(results, columns=['text', 'date', 'url'])
    results_df.to_csv(csv_name, index=False)

    return results_df

if __name__ == '__main__':
    # # create a crawler object containing all urls of domain indymedia.nl
    # indy_media_crawler = WappieCrawler(website_queue=['https://www.indymedia.nl/'], wait_time=1, max_visits=10)
    # indy_media_crawler.go()
    # # Scrape based on text search
    # indy_media_df = scrape_df_and_csv(indy_media_crawler, csv_name='results_indymedia.csv', date_time_text_search='gepost door:')
    #
    # niburu_crawler = WappieCrawler(website_queue=['https://niburu.co/'], wait_time=1, max_visits=10)
    # niburu_crawler.go()
    # # Scrape based on time element
    # niburu_df = scrape_df_and_csv(niburu_crawler, csv_name='results_niburu.csv')


    # Gives you a random post every time when crawling.
    # Found a workaround by using the Copy All Tab Urls extension in firefox and opening a bunch of them
    # does require some manual work, but it may be worth it for analysis
    # I could just paste all urls in Pycharm and use ctrl+shift+j to concatenate the urls to one line. Separating them with '; '
    # nine_for_news_url_string = 'https://www.ninefornews.nl/page/13/; https://www.ninefornews.nl/europarlementarier-geeft-in-3-minuten-3-redenen-waarom-wereldwijd-pandemieverdrag-gevaarlijk-is/; https://www.ninefornews.nl/world-economic-forum-kondigt-zomer-davos-aan-en-hier-vindt-de-bijeenkomst-plaats/; https://www.ninefornews.nl/russische-soldaten-doen-opmerkelijke-uitspraken-over-oorlog-in-oekraine/; https://www.ninefornews.nl/harde-uithaal-naar-groene-gek-timmermans-hele-gevaarlijke-man/; https://www.ninefornews.nl/zo-hebben-ze-de-pandemie-nog-2-jaar-gerekt-dit-is-een-groot-schandaal/; https://www.ninefornews.nl/brisante-onthullingen-de-hufterigheid-van-rutte-cum-suis-kent-geen-grenzen/; https://www.ninefornews.nl/kaag-kiest-er-bewust-voor-om-de-nederlandse-bevolking-armer-te-maken/; https://www.ninefornews.nl/verslagenheid-na-aannemen-dictatoriale-pandemiewet-moeilijke-moeilijke-tijden-komen-eraan/; https://www.ninefornews.nl/instagram-influencer-verheerlijkt-euthanasie-heb-je-er-zin-in/; https://www.ninefornews.nl/timmermans-aangepakt-trek-die-verschrikkelijke-nederland-op-slot-wet-in/; https://www.ninefornews.nl/thierry-baudet-waarschuwt-ze-laten-nadrukkelijk-de-mogelijkheid-voor-klimaatlockdowns-open/; https://www.ninefornews.nl/eerste-kamerlid-christenunie-gaat-zonder-enig-benul-over-omstreden-pandemiewet-stemmen/; https://www.ninefornews.nl/fel-verzet-tegen-pandemiewet-geef-onze-vrijheid-niet-weg/; https://www.ninefornews.nl/schrijver-hier-heeft-het-duivelsgebroed-zich-in-nederland-genesteld/; https://www.ninefornews.nl/amerikaanse-acteur-doet-schokkend-boekje-open-over-luguber-ritueel-dat-hij-zag/; https://www.ninefornews.nl/fvd-stelt-kamervragen-over-bilderbergconferentie-waarom-krijgt-de-kamer-niets-te-horen/; https://www.ninefornews.nl/de-boeren-moeten-weg-want-rutte-wil-iets-heel-speciaals-samen-met-het-world-economic-forum/; https://www.ninefornews.nl/gevaccineerden-zullen-over-2-jaar-dood-zijn-zegt-deze-arts/; https://www.ninefornews.nl/europarlementarier-dit-is-waarom-de-who-bestempeld-moet-worden-als-terreurorganisatie/; https://www.ninefornews.nl/arts-over-nederlanders-die-heulen-met-perverse-terreur-van-von-der-leyen-en-schwab-pak-ze-aan/; https://www.ninefornews.nl/rusland-dreigt-onze-f-16s-uit-de-lucht-te-schieten-boven-oekraine/; https://www.ninefornews.nl/oekraine-doet-schokkende-bekentenis-die-is-genegeerd-door-westerse-media/; https://www.ninefornews.nl/nieuwe-pensioenwet-gekraakt-wanneer-zoiets-in-een-derdewereldland-zou-gebeuren-zouden-de-rapen-gaar-zijn/; https://www.ninefornews.nl/europese-hoofd-van-bilderberg-victor-halberstadt-ontkent-bij-bilderberg-dat-hij-victor-halberstadt-is/; https://www.ninefornews.nl/coronacriticus-van-het-eerste-uur-rashid-buttar-vlak-voor-zijn-dood-ik-ben-doelbewust-vergiftigd/; https://www.ninefornews.nl/acteur-epstein-eiland-is-niet-het-enige-eiland-waar-ze-kinderen-pijn-hebben-gedaan/; https://www.ninefornews.nl/kamerlid-haalt-fel-uit-naar-d66-die-partij-is-een-dogmatische-sekte/; https://www.ninefornews.nl/advocaat-zegt-groenlinks-lidmaatschap-op-omdat-klaver-en-halsema-aangesloten-zijn-bij-world-economic-forum/; https://www.ninefornews.nl/great-reset-architect-yuval-harari-glipt-via-achterdeur-naar-binnen-bij-bilderberg/; https://www.ninefornews.nl/slachtoffers-prikschade-gaan-langs-bij-ministerie-van-vws-wil-je-meedoen-pak-je-kans/; https://www.ninefornews.nl/rutte-en-kaag-krijgen-bakken-kritiek-om-deelname-bilderbergconferentie-zij-zijn-bij-ons-in-dienst/; https://www.ninefornews.nl/rutte-maakt-zich-niet-populair-u-wilt-gewoon-escaleren/; https://www.ninefornews.nl/sucharit-bhakdi-hoe-rna-prikken-je-permanent-genetisch-transformeren/; https://www.ninefornews.nl/veiligheidschef-radioactieve-wolk-drijft-richting-west-europa/; https://www.ninefornews.nl/video-elon-musk-geeft-journalist-een-lesje-in-complottheorieen/; https://www.ninefornews.nl/topacteur-komt-met-baanbrekende-film-over-kinderhandel-er-komt-een-grote-storm-aan-en-dat-weten-ze/; https://www.ninefornews.nl/kijk-rutte-en-kaag-onder-politiebegeleiding-naar-schimmige-bilderbergconferentie/; https://www.ninefornews.nl/bilderberg-2023-van-start-deze-nederlanders-zijn-van-de-partij/; https://www.ninefornews.nl/volgens-president-zelenski-wordt-alles-op-de-krim-kapotgeschoten-zo-is-de-situatie-echt/; https://www.ninefornews.nl/kijk-deze-explainer-tristate-city-was-toch-een-complottheorie/; https://www.ninefornews.nl/de-onderschatte-gezondheidsvoordelen-van-medicinale-cannabis/; https://www.ninefornews.nl/financieel-expert-over-nieuwe-pensioenwet-dat-is-echt-een-kulverhaal-er-zit-een-andere-agenda-achter/; https://www.ninefornews.nl/overgrote-deel-nederlanders-heeft-totaal-geen-idee-van-wat-zich-op-dit-moment-onder-hun-neus-af-aan-het-spelen-is/; https://www.ninefornews.nl/uitbreiding-sleepwet-maakt-nederland-surveillance-staat/; https://www.ninefornews.nl/kolonel-niemand-kan-een-hypersonische-raket-neerhalen-dat-is-gewoon-absurd/; https://www.ninefornews.nl/het-social-media-complot-van-de-jonge-wat-kan-die-man-uniek-makkelijk-liegen-angstaanjagend-gewoon/; https://www.ninefornews.nl/musk-haalt-uit-naar-magneto-george-soros-hij-haat-de-mensheid/; https://www.ninefornews.nl/hier-komt-de-geheimzinnige-bilderberggroep-deze-week-bijeen-en-rutte-is-erbij/; https://www.ninefornews.nl/vader-van-elon-musk-doet-opmerkelijke-uitspraken-over-ontvolkingsplannen-bill-gates/; https://www.ninefornews.nl/wereldwijd-evenement-tegen-de-globalisten-op-20-mei-we-zijn-er-klaar-voor-kom-maar-op/; https://www.ninefornews.nl/aartsbisschop-pleit-voor-verbond-tegen-davos-lobby-en-world-economic-forum-we-voeren-een-historisch-gevecht/; https://www.ninefornews.nl/npo-verspreidde-complottheorie-en-martin-bosma-wilde-een-debat-kijk-naar-de-reacties/; https://www.ninefornews.nl/beelden-klimaatactivisten-roepen-op-de-uva-op-tot-geweld-en-vermoorden-van-joden/; https://www.ninefornews.nl/houdt-kuipers-modellen-en-data-van-rivm-achter-om-pandemiewet-door-te-drukken/; https://www.ninefornews.nl/journalistiek-schandaal-van-de-hoogste-orde-maakt-tongen-los-kamerdebat-aangevraagd/; https://www.ninefornews.nl/terwijl-burgers-nauwlettend-worden-gecontroleerd-smijt-dit-kabinet-zonder-controle-met-miljarden/; https://www.ninefornews.nl/kuipers-bevestigt-hier-dat-hij-elke-maatregel-die-hij-zou-willen-gebruiken-alsnog-kan-invoeren/; https://www.ninefornews.nl/vvd-senator-liegt-in-eerste-kamer-vuile-leugenaar-ik-was-daar-mevrouw/; https://www.ninefornews.nl/fdf-voorman-roept-op-prepare-for-battle/; https://www.ninefornews.nl/eerste-kamerlid-stipt-hier-een-pijnlijk-punt-aan-over-de-pandemiewet/; https://www.ninefornews.nl/nooit-vergeten-deze-partijen-hielden-de-mogelijkheid-open-voor-het-opsluiten-van-ongevaccineerden/; https://www.ninefornews.nl/filmpje-klaus-schwab-heeft-skeletten-in-de-kast/; https://www.ninefornews.nl/schandalig-dat-deze-wetten-zo-kort-voor-de-installatie-van-de-nieuwe-eerste-kamer-worden-behandeld/; https://www.ninefornews.nl/de-boodschap-is-duidelijk-mensen-zijn-erin-genaaid/; https://www.ninefornews.nl/columnist-maakt-gideon-van-meijeren-uit-voor-dwergnazi-en-populistische-pisvlek/; https://www.ninefornews.nl/financieel-expert-over-grootste-schandaal-ooit-het-zit-ontzettend-fout-met-de-pensioenfondsen/; https://www.ninefornews.nl/uitvinder-mrna-vaccins-haalt-uit-naar-klaus-schwab-hij-is-een-fascist/; https://www.ninefornews.nl/einde-van-eigen-auto-in-zicht-you-will-own-nothing/; https://www.ninefornews.nl/zo-zien-vrijgegeven-wob-documenten-over-de-bestrijding-van-desinformatie-eruit/; https://www.ninefornews.nl/dit-is-de-meest-dictatoriale-wet-die-ooit-door-een-regering-is-voorgesteld/; https://www.ninefornews.nl/kijk-kuipers-heeft-even-geen-tijd-voor-vraag-over-aansprakelijkheid-bij-vaccinatieschade/; https://www.ninefornews.nl/kaag-onderbroken-op-d66-partijcongres-ik-voel-mij-verraden-door-u/; https://www.ninefornews.nl/senator-over-grooming-van-kinderen-door-vn-who-tijd-om-te-vertrekken-uit-het-paradijs-van-viespeuken/; https://www.ninefornews.nl/hongaarse-premier-vergelijkt-eu-met-hitlers-plannen-voor-wereldheerschappij/; https://www.ninefornews.nl/ernstige-zorgen-om-drinkwatertekort-in-nederland-dit-zit-er-achter/; https://www.ninefornews.nl/omtzigt-maakt-hier-een-belangrijk-punt-over-aansprakelijkheid-bij-vaccinschade/; https://www.ninefornews.nl/europarlementarier-de-boeren-moeten-verdwijnen-uit-europa-en-dit-voedsel-komt-er-voor-terug/; https://www.ninefornews.nl/europarlementarier-de-boeren-moeten-verdwijnen-uit-europa-en-dit-voedsel-komt-er-voor-terug/; https://www.ninefornews.nl/de-jonge-zou-zich-morgen-moeten-melden-bij-de-tweede-kamer-om-onder-ede-te-worden-gehoord/; https://www.ninefornews.nl/omt-lid-onder-vuur-deze-man-moet-je-echt-zijn-registratie-afpakken/; https://www.ninefornews.nl/immunoloog-waarschuwt-er-komt-iets-nieuws-op-ons-af/; https://www.ninefornews.nl/eerste-kamerleden-staan-aan-de-vooravond-van-de-belangrijkste-beslissing-in-hun-leven/; https://www.ninefornews.nl/wordt-deze-voorzitter-van-world-economic-forum-werkgroep-de-nieuwe-directeur-van-twitter/; https://www.ninefornews.nl/vvd-kamerlid-doet-lacherig-over-huisartsen-die-tijdens-corona-werden-gecensureerd/; https://www.ninefornews.nl/brisant-check-martin-bosma-over-de-duistere-verwevenheid-van-d66-met-dit-lobbykantoor/; https://www.ninefornews.nl/van-haga-woest-dit-zijn-toch-de-zaken-die-niet-gezegd-mogen-worden/; https://www.ninefornews.nl/advocaat-we-moeten-ons-verzetten-tegen-de-pandemiewet-en-wel-hierom/; https://www.ninefornews.nl/kijk-europarlementarier-legt-ten-overstaan-van-het-parlement-de-ware-agenda-bloot/; https://www.ninefornews.nl/europarlementarier-doorprikt-keiharde-leugens-eu-stop-met-de-klimaatdictatuur/; https://www.ninefornews.nl/wie-is-er-aansprakelijk-voor-vaccinatieschade-luister-naar-kuipers/; https://www.ninefornews.nl/kamerlid-deelt-flinke-sneer-uit-aan-vvd-partij-van-oplichters-een-oplichtersbende/; https://www.ninefornews.nl/regering-kan-instemmen-met-wetgeving-zonder-dat-parlement-akkoord-is-buitengewoon-problematisch/; https://www.ninefornews.nl/deze-great-food-reset-leidt-in-nederland-tot-schrijnende-taferelen/'
    #
    # # Turn giant string into list of separate url strings
    # nine_for_news_urls = extract_urls_from_single_string(nine_for_news_url_string)
    # nine_for_news_crawler = WappieCrawler(website_queue=[])
    #
    # # add urls to urls_to_scrape
    # nine_for_news_crawler.urls_to_scrape = nine_for_news_urls
    #
    # # Scrape nine for news based on class search
    # nine_for_news_df = scrape_df_and_csv(nine_for_news_crawler, csv_name='results_nine_for_news.csv', date_time_class_search=['span', 'date meta-item tie-icon'])

    transitieweb_crawler = WappieCrawler(website_queue=['https://www.transitieweb.nl/'], wait_time=1, max_visits=10)
    transitieweb_crawler.go()
    # Scrape based on time element
    transitieweb_df = scrape_df_and_csv(transitieweb_crawler, csv_name='results_transitieweb.csv', date_time_class_search=['span', 'published'])

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
