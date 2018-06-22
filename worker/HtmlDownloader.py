import requests
from worker import RedisWorker
import time
from setting import *
import aiohttp
import asyncio
import traceback

# conn = aiohttp.TCPConnector(limit=30)
sem = asyncio.Semaphore(30)


class HtmlDownloader(object):
    def __init__(self, proxy_bool=None):
        self.bool = proxy_bool

    def _get_ip(self):
        url = 'http://127.0.0.1:5555/ip'
        ip = requests.get(url).text
        proxy = {
            'http': ip,
            'https': ip,
        }
        return proxy

    async def download(self, url):
        if self.bool == True:
            self.proxy = self._get_ip()
        else:
            self.proxy = None
        if url is None:
            return None

        while True:
            try:
                async with aiohttp.ClientSession() as session:
                    async with sem:
                        async with session.get(url, headers=HEADERS, proxy=self.proxy, timeout=2) as res:
                            if res.status == 200:
                                RedisWorker.redisdb.put_old(url)
                                return await res.text()
                            else:
                                logger.warning(res.status)

                            time.sleep(0.5)
            except:
                # print(traceback.format_exc())
                pass
