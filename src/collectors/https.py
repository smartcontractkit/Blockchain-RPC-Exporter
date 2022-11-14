import requests
from settings import logger
from helpers import strip_url
from time import perf_counter
from configuration import cfg

class https_connection():

    def __init__(self, url):
        self.url, self.stripped_url = url, strip_url(url)

    def is_connected_post_check(self, payload):
        try:
            response = requests.post(self.url, json=payload, timeout=cfg.response_timeout)
            response.raise_for_status()
        except (IOError, requests.HTTPError) as exc:
            logger.error(exc, url=self.stripped_url)
            return False
        return response.ok

    def get_latency(self, payload):
        start = perf_counter()
        response = requests.post(self.url, json=payload)
        return (perf_counter() - start) * 1000
