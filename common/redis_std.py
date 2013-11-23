import logging
import ujson
from redis_std import Redis
from common.thread_locals import get_thread_var, set_thread_var

logger = logging.getLogger('redis')

class RedisManager(object):
    def __init__(self, connection = 'redis', channel='redis_channel'):
        self.connection = connection
        self.channel = channel

    def redis_write(self, key, val):
        self.redis_get().set(key, ujson.dumps(val))


    def redis_read(self, key, default=None):
        val = self.redis_get().get(key)
        if val is None:
            return default
        return ujson.loads(self.redis_get().get(key))


    def redis_publish(self, val):
        self.redis_get().publish(self.channel, ujson.dumps(val))


    def redis_get(self):
        redis = get_thread_var(self.connection)
        if not redis:
            redis = Redis()
            set_thread_var(self.connection, redis)

        return redis

