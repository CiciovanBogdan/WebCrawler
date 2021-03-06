import logging
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup


def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    file_handler = logging.FileHandler("Random.log")
    file_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(message)s"))
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s:%(message)s"))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)


class FailToCrawl(Exception):
    pass


def download_url(url):
    return requests.get(url).text


def get_linked_urls(url, html):
    soup = BeautifulSoup(html, 'html.parser')
    for link in soup.find_all('a'):
        path = link.get('href')
        if path and path.startswith('/'):
            path = urljoin(url, path)
        yield path


class Crawler:

    def __init__(self, urls=None):
        if urls is None:
            urls = []
        self.visited_urls = []
        self.urls_to_visit = urls

    def add_url_to_visit(self, url):
        if url not in self.visited_urls and url not in self.urls_to_visit:
            self.urls_to_visit.append(url)

    def crawl(self, url):
        html = download_url(url)
        for url in get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.urls_to_visit:
            url = self.urls_to_visit.pop(0)
            logging.info(f'Crawling: {url}')
            try:
                self.crawl(url)
            except FailToCrawl:
                logging.exception(f'Failed to crawl: {url}')
            finally:
                self.visited_urls.append(url)


if __name__ == '__main__':
    configure_logging()
    Crawler(urls=['https://www.google.ro/']).run()
