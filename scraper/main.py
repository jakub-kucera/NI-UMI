import argparse
import threading
from dataclasses import dataclass
from datetime import datetime
from queue import Queue
from urllib.parse import urljoin, urlparse

import requests
import validators
from bs4 import BeautifulSoup

# includes a user-agent in the header, because some websites block requests without one
REQUESTS_HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36',
}

FORBIDDEN_FILE_TYPES = ['pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx', 'zip', 'rar', '7z', 'tar', 'gz', 'bz2', 'mp3', 'mp4', 'avi', 'mkv', 'flv', 'wmv', 'mov', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'ico', 'psd', 'ai', 'eps', 'tif', 'tiff', 'wav', 'mp3', 'ogg', 'flac', 'aac', 'wma', 'm4a', 'exe', 'dll', 'deb', 'rpm', 'apk', 'iso', 'dmg', 'odt', 'txt', 'csv', 'tsv']

DEFAULT_START_URL = "https://fit.cvut.cz/"
DEFAULT_END_URL = "https://www.mit.edu/"
# DEFAULT_END_URL_CORE = '.'.join(urlparse(DEFAULT_END_URL).netloc.split('.')[-2:])


# global variables for collections of opened and closed nodes
opened: set['Node'] = set()
closed: set['Node'] = set()


def score_url(url: str, prev_url: str):
    """Scores a url in order to help the search. In terms of A* this would be the heurestic function"""
    score = 0
    # prioritise pages with an 'edu' domain
    if urlparse(url).netloc.split('.')[-1] != 'edu':
        score += 10

    # prioritise urls from a different domain
    if urlparse(url).netloc == urlparse(prev_url).netloc:
        score += 2

    # # the above recognises different subdomains as different domains, so this checks only for L2 and L1 domains
    # if urlparse(url).netloc.split('.')[-2:] == urlparse(prev_url).netloc.split('.')[-2:]:
    #     score += 1

    # prioritise HTTPS urls
    if urlparse(url).scheme == 'http':
        score += 2

    return score


def skip_url(url: str):
    """Determines whether an url should be skipped or not"""
    if not validators.url(url):
        return True

    file_extension = url.split('.')[-1]
    if file_extension in FORBIDDEN_FILE_TYPES:
        return True

    return False


class Node:
    """
    A Node which represents 1 url and some metadata about it.
    """
    def __init__(self, url: str, parent: 'Node'):
        self.url: str = url
        self.parent: Node = parent
        self.steps = parent.steps + 1 if parent else 0
        self.url_score = score_url(url, parent.url) if parent else 0
        self.total_score = self.steps + self.url_score

    # the hash and equal methods are overridden so that when Node is stored in a set, it is only identified by the `url` attribute
    def __key(self):
        return self.url

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.__key() == other.__key()
        return NotImplemented


def run(end_url_core: str):
    while len(opened) > 0:
        # get the node with the lowest score
        current_node = min(opened, key=lambda x: x.total_score)

        # push to closed nodes.
        # (This was moved here from the end of the loop, to improve behaviour during
        # parallel computing, which was eventually deleted since it was not needed.)
        closed.add(current_node)
        # remove from opened nodes
        opened.remove(current_node)
        url = current_node.url

        print(20*'=')
        print(f"visiting {url}")
        print(f"prev url {current_node.parent.url if current_node.parent else None}")
        print(f"{current_node.steps} + {current_node.url_score} = {current_node.total_score}")
        print(f"opened: {len(opened)} | closed: {len(closed)}")

        # get the content of the page
        try:
            r = requests.get(url, headers=REQUESTS_HEADERS)
        except requests.exceptions.SSLError:
            try:
                r = requests.get(url, headers=REQUESTS_HEADERS, verify=False)
            except requests.exceptions.ConnectionError:
                print(f"<====== Connection error for {url}")
                continue
        except requests.exceptions.ConnectionError:
            print(f"<====== Connection error for {url}")
            continue

        # parse the content
        soup = BeautifulSoup(r.text, 'html.parser')
        # find all links on the page
        new_urls = soup.findAll('a')
        for new_urls_raw in new_urls:
            new_url = new_urls_raw.get('href')

            # if new_url points to the same page, it is of a relative path, so it needs to be joined.
            # (if url and new_url are of a different domain, urljoin will return new_url)
            joined_new_url = urljoin(url, new_url)

            if skip_url(joined_new_url):
                continue

            discovered_node = Node(joined_new_url, current_node)
            # check if this url node has been already discovered before
            if discovered_node not in opened and discovered_node not in closed:
                opened.add(discovered_node)

                # check if the url is the END_URL
                if end_url_core in joined_new_url:
                    print(f"FOUND: {joined_new_url}")
                    return discovered_node

    return None


def print_path(node: Node):
    if node.parent:
        print_path(node.parent)
    print(node.url, end=' -> ')


def main(start_url: str, end_url: str):
    start = datetime.now()

    # # add the HTTPS prefix if it is missing
    # start_url = urlparse(start_url, 'https').geturl()
    # end_url = urlparse(end_url, 'https').geturl()

    start_node = Node(start_url, None)
    opened.add(start_node)

    end_url_core = '.'.join(urlparse(end_url).netloc.split('.')[-2:])
    # the searching part
    dest_node = run(end_url_core)

    print(60*'=')
    print_path(dest_node)


    print(f"\nTime taken: {datetime.now() - start}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(prog='scraper.py', description="This program scrawls the web and find a path from a given start url to an end url.")
    parser.add_argument('-s', '--start', action='store', default=DEFAULT_START_URL,
                        metavar='START', type=str,
                        help='The start url. Include the HTTPS/HTTP prefix. Default: ' + DEFAULT_START_URL)
    parser.add_argument('-e', '--end', action='store', default=DEFAULT_END_URL,
                        metavar='END', type=str,
                        help='The end url. Include the HTTPS/HTTP prefix. Default: ' + DEFAULT_END_URL)

    args = parser.parse_args()
    main(start_url=args.start, end_url=args.end)
