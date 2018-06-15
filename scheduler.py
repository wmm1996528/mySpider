import my_wokres.RedisWorker
from my_wokres.HtmlDownloader import HtmlDownloader
from my_wokres.HtmlParser import HtmlParser
from my_wokres.DataOutput import DataOutput
from multiprocessing import Process
from setting import *
import time
import sys

sys.path.append("..")


class Spiders():
    def __init__(self):
        self.r = my_wokres.RedisWorker.redisQueue('new')
        self.html = HtmlDownloader(None)
        self.parser = HtmlParser()
        self.dataout = DataOutput()
        self.r.put(URLS)

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

    def run(self):
        if THREADBOOL:
            self.process_start()
        else:
            self.start()


spider = Spiders()
if __name__ == '__main__':
    work = Spiders()
    work.run()
    # t1 = time.time()
    # for i in range(10):
    #     t = Thread(target=my_wokres.start, args=())
    #     threads.append(t)
    # for i in range(len(threads)):
    #     print('线程% running...' % i)
    #     threads[i].start()
    #
    # for i in range(len(threads)):
    #
    #     threads[i].join()
    #     print('线程% close...' % i)
    # t2 = time.time()
    # print(t2-t1)
