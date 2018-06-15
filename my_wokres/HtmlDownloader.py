import requests
from my_wokres import RedisWorker
import time
from setting import *


class HtmlDownloader(object):
    def __init__(self, proxy_bool=None):
        self.session = requests.session()
        self.bool = proxy_bool

    def _get_ip(self):
        url = 'http://127.0.0.1:5555/ip'
        ip = requests.get(url).text
        proxy = {
            'http': ip,
            'https': ip,
        }
        return proxy

    def download(self, url):
        if self.bool == True:
            self.proxy = self._get_ip()
        else:
            self.proxy = None
        if url is None:
            return None

        while True:
            res = self.session.get(url, headers=HEADERS, proxies=self.proxy)
            if res.status_code == 200:
                RedisWorker.redisdb.put_old(url)
                return res.text
            else:
                logger.warning(res.status_code)

            time.sleep(0.5)
