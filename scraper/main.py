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

START_URL = "https://fit.cvut.cz/"
END_URL = "https://www.mit.edu/"
END_URL_CORE = '.'.join(urlparse(END_URL).netloc.split('.')[-2:])


def score_url(url: str, prev_url: str):
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
    if not validators.url(url):
        return True

    file_extension = url.split('.')[-1]
    if file_extension in FORBIDDEN_FILE_TYPES:
        return True

    return False


class Node:
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


opened: set[Node] = set()
closed: set[Node] = set()


def worker():
    while len(opened) > 0:
        current_node = min(opened, key=lambda x: x.total_score)
        closed.add(current_node)
        opened.remove(current_node)
        url = current_node.url

        print(20*'=')
        print(f"visiting {url}")
        print(f"prev url {current_node.parent.url if current_node.parent else None}")
        print(f"{current_node.steps} + {current_node.url_score} = {current_node.total_score}")
        print(f"opened: {len(opened)} | closed: {len(closed)}")

        request_start = datetime.now()
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
        request_end = datetime.now()
        print(f"request time: {request_end - request_start}")

        soup = BeautifulSoup(r.text, 'html.parser')
        new_urls = soup.findAll('a')
        for new_urls_raw in new_urls:
            new_url = new_urls_raw.get('href')
            # if new_url points to the same page, it is of a relative path, so it needs to be joined.
            # (if url and new_url are of a different domain, urljoin will return new_url)
            joined_new_url = urljoin(url, new_url)

            if skip_url(joined_new_url):
                continue

            discovered_node = Node(joined_new_url, current_node)
            if discovered_node not in opened and discovered_node not in closed:
                opened.add(discovered_node)

                if END_URL_CORE in joined_new_url:
                    print(f"FOUND: {joined_new_url}")
                    # opened.clear()
                    return discovered_node

    return None


def print_path(node: Node):
    if node.parent:
        print_path(node.parent)
    print(node.url, end=' -> ')


def run():
    start = datetime.now()
    start_node = Node(START_URL, None)
    opened.add(start_node)

    # the searching part
    dest_node = worker()

    print(60*'=')
    print_path(dest_node)

    print(f"\nTime taken: {datetime.now() - start}")


if __name__ == '__main__':
    run()
