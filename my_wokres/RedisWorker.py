import redis
from setting import *


class redisQueue:
    def __init__(self, name, namespace='my'):
        self.__db = redis.from_url(REDIS_URL)
        self.key = '%s' % name
        self.old = 'old'

    def get_size(self):

        return self.__db.scard(self.key)

    def put(self, item):
        if isinstance(item, str):
            self.__db.sadd(self.key, item)
        elif isinstance(item, list):
            for i in item:
                self.__db.sadd(self.key, i)

    def put_old(self, item):
        if not self.__db.sismember(self.old, item):
            self.__db.sadd(self.old, item)

    def get_wait(self):
        while True:
            item = self.__db.spop(self.key)
            if item:
                return item

    def get_nowait(self):
        item = self.__db.spop(self.key)
        return item

    def get_all(self):
        return self.__db.smembers(self.key)

    def get_old(self):
        return self.__db.scard(self.old)

    def get_all_num(self):
        return self.__db.scard(self.key) + self.__db.scard(self.old)

    def set_monit(self, data):
        self.__db.sadd('monit', data)

    def get_monit(self):
        self.__db.spop('monit')


redisdb = redisQueue('old')
