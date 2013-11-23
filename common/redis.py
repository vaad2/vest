import logging
import ujson
from redis import Redis
from common.thread_locals import get_thread_var, set_thread_var

logger = logging.getLogger('redis')


def redis_write(key, val):
    redis_get().set(key, ujson.dumps(val))


def redis_read(key, default=None):
    val = redis_get().get(key)
    if val is None:
        return default
    return ujson.loads(redis_get().get(key))


def redis_publish(channel, val):
    redis_get().publish(channel, ujson.dumps(val))


def redis_get(connection='redis'):
    redis = get_thread_var(connection)
    if not redis:
        redis = Redis()
        set_thread_var(connection, redis)

    return redis

