import requests
import time
import random

import bs4

URL = 'https://arxiv.org/abs/%s'

class Throttle:
    def __init__(self, interval: float, jitter_proportion: float = .3):
        self.interval = interval
        self.jitter = jitter_proportion * interval
        self.next_good = 0.0
    
    def wait(self):
        cooldown = self.next_good - time.time()
        if cooldown > 0:
            time.sleep(cooldown)
        self.next_good = time.time() + self.interval + random.uniform(
            0, self.jitter, 
        )

def scrapeAbsFromArxiv(throttle: Throttle, arxiv_id: str):
    throttle.wait()
    arxiv_id = arxiv_id.lower()
    PREFIX = 'arxiv:'
    if arxiv_id.startswith(PREFIX):
        arxiv_id = arxiv_id[len(PREFIX):]
    url = URL % arxiv_id
    res = requests.get(url)
    soup = bs4.BeautifulSoup(res.text, 'html.parser')
    meta_tag = soup.find('meta', attrs={'name': 'citation_abstract'})
    import pdb; pdb.set_trace()
    if meta_tag is None:
        return None
    assert isinstance(meta_tag, bs4.element.Tag)
    return meta_tag['content']
