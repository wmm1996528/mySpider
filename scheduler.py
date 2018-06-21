import my_wokres.RedisWorker
from my_wokres.HtmlDownloader import HtmlDownloader
from my_wokres.HtmlParser import HtmlParser
from my_wokres.DataOutput import DataOutput
from multiprocessing import Process
from threading import Thread
from setting import *
import time
import sys
import os
import asyncio
from app.monitoring import app


def costTime(func):
    def wrapper(*args, **kwargs):
        t1 = time.time()
        func(*args, **kwargs)
        t2 = time.time()
        print(t2 - t1)

    return wrapper


sys.path.append("..")


class Spiders():
    def __init__(self):
        self.r = my_wokres.RedisWorker.redisQueue('new')
        self.html = HtmlDownloader(None)
        self.parser = HtmlParser()
        self.dataout = DataOutput()
        self.r.put(URLS)
        self.app = app

    def start(self):
        while self.r.get_size() != 0:
            url = self.r.get_wait()

            html = self.html.download(url)
            data = self.parser.parser(url, html)
            self.dataout.output_mongo(data)

    def process_start(self):
        process = []
        for i in range(THREADNUM):
            p = Process(target=self.start, args=())
            process.append(p)
        for i in range(THREADNUM):
            logger.info('Process %s running........' % i)
            process[i].start()
        for i in range(THREADNUM):
            process[i].join()
            logger.info('Process %s completed........' % i)

    @costTime
    def run(self):
        if THREADBOOL:
            self.process_start()
        else:
            self.start()

    async def asyncrun(self, url):
        # print(url)
        html = await self.html.download(url)
        data = self.parser.parser(url, html)
        # print(data)
        self.dataout.output_mongo(data)

    def cost(self, data):
        while True:
            allUrl = self.r.get_size()
            now = self.r.get_old()
            if now == allUrl:
                scheduledTime = '10000'
            time.sleep(1)
            after = self.r.get_old()
            # print(now, after)
            speed = after - now
            wait = allUrl - now
            print(wait)
            # print(allUrl - after)
            # print(speed)
            if wait == 0:

                try:
                    scheduledTime = str((allUrl - after) // speed)
                except:
                    scheduledTime = '已完成'
                data.update({
                    'timeNum': scheduledTime,
                    'progess': str(round((after / allUrl) * 100, 3)),
                    'nowNum': after,
                    'wait': wait
                })
                self.r.set_monit(data)
                os._exit(0)
                break
            else:
                scheduledTime = str((allUrl - after) // speed)
                data.update({
                    'timeNum': scheduledTime,
                    'progess': str(round((after / allUrl) * 100, 3)),
                    'nowNum': after,
                    'wait': wait
                })
                self.r.set_monit(data)

    @costTime
    def eventLoop(self):
        urls = [i.decode() for i in self.r.get_all()]
        tasks = [self.asyncrun(url) for url in urls]
        loop = asyncio.get_event_loop()
        loop.run_until_complete(asyncio.wait(tasks))

    def start_monit(self):

        self.app.run(port=2121)

    def eventRun(self):
        p = Thread(target=self.start_monit, args=())
        p.start()
        data = {}
        t = Thread(target=self.cost, args=(data,))
        t.start()
        self.eventLoop()


spider = Spiders()
if __name__ == '__main__':
    work = Spiders()
    work.eventRun()

    # def sua():
    #     n = 0
    #     for i in range(1000):
    #         n += i
    #
    #
    # sua()
