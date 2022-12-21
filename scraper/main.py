import threading
from dataclasses import dataclass
from queue import Queue
from urllib.parse import urljoin, urlparse

import requests
import validators
from bs4 import BeautifulSoup

START_URL = "https://fit.cvut.cz/"
END_URL = "https://www.mit.edu/"
# END_URL = "www.mit.edu"


def score_url(url: str, prev_url: str):
    score = 0  # TODO + path
    # prioritise pages with an 'edu' domain
    if urlparse(url).netloc.split('.')[-1] != 'edu':
        score += 10
    # prioritise urls from a different domain
    if urlparse(url).netloc == urlparse(prev_url).netloc:
        score += 2

    if urlparse(url).scheme == 'http':
        score += 2


# @dataclass(order=True)
class Node:
    def __init__(self, url: str, parent: 'Node'):
        self.url: str = url
        self.parent: Node = parent
        self.steps = parent.steps + 1 if parent else 0
        self.url_score = score_url(url, parent.url) if parent else 0
        self.total_score = self.steps + self.url_score
    # url: str
    # steps: int
    # url_score: int
    # total_score: int
    # parent: 'Node' = None

    def __key(self):
        return self.url

    def __hash__(self):
        return hash(self.__key())

    def __eq__(self, other):
        if isinstance(other, Node):
            return self.__key() == other.__key()
        return NotImplemented


# queue = Queue()
# {url: prev_url}
# opened: dict[str, str] = dict()
opened: set[Node] = set()
closed: set[Node] = set()
# visited = set()  # do I even need this

min(opened, key=lambda x: x.total_score)

def worker():
    while True:
        # TODO pop
        # url = queue[0]
        url = queue.get()
        print(f"visiting {url}")
        print(f"queue size: {queue.qsize()}")
        print(f"discovered size: {len(discovered)}")
        print(f"visited size: {len(visited)}")
        r = requests.get(url)
        soup = BeautifulSoup(r.text, 'html.parser')
        links = soup.findAll('a')
        for link_raw in links:
            link = link_raw.get('href')
            joined_url = urljoin(url, link)

            is_valid = validators.url(joined_url)
            if not is_valid:
                # print(f"invalid url {joined_url}")
                continue

            # print(link)
            # print(joined_url)
            # print(20*'=')

            if "mit.edu" in joined_url:
                print("FOUND")
                return

            if joined_url not in discovered and joined_url not in visited:
                queue.put(joined_url)
                discovered[joined_url] = url
            # else:
            #     print(f"already visited {joined_url}")

            # print(link.get('href'))
        visited.add(url)


def run():
    # queue = Queue()
    queue.put(START_URL)
    discovered[START_URL] = None
    workers = []

    for _ in range(30):
        t = threading.Thread(target=worker, daemon=True)
        t.start()
        workers.append(t)
    # visited = []

    queue.join()
    print('All work completed')


if __name__ == '__main__':
    run()
