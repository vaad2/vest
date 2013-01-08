from thread_locals import get_thread_var, set_thread_var
from django.utils.datastructures import SortedDict

def mongo_get(collection = None):
    from django.conf import settings
    from pymongo import Connection
    connection = get_thread_var('mongo_connection')

    if not connection:
        connection = Connection()[settings.MONGO['default']['NAME']]
        set_thread_var('mongo_connection', connection)

    if connection:
        if hasattr(collection, '_meta'):
            return connection[collection._meta.db_table]
        return connection[collection]

    return connection


def truncate(model_or_table):
    from django.db import connection
    cursor = connection.cursor()

    if hasattr(model_or_table, '_meta'):
        model_or_table = model_or_table._meta.db_table

    cursor.execute("TRUNCATE TABLE `%s`" % model_or_table)

class MongoQuerysetWrapper(object):
    def __init__(self, cursor):
        self._cursor = cursor

    def __len__(self):
        return self._cursor.count()

    def __getslice__(self, x, y):
        return self._cursor.skip(x).limit(y - x)

    def __iter__(self):
        return self

    def next(self):
        for item in self._cursor:
            return item
        raise StopIteration

    def count(self):
        return len(self)


def qset_to_dict(qset, key = 'id'):
    res = SortedDict()
    for item in qset:
        res[getattr(item, key)] = item
    return res