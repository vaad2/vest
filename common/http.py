import json
try:
    from bson import json_util
    from bson.objectid import ObjectId
except BaseException,e:
    pass

from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponse
from json import JSONEncoder
# from django.utils.simplejson.encoder import JSONEncoder
try:
    import ujson
except BaseException, e:
    pass

class MongoEncoder(JSONEncoder):
    def default(self, obj, **kwargs):
        if isinstance(obj, ObjectId):
            return str(obj)
        else:
            return JSONEncoder.default(obj, **kwargs)

# , default=json_util.default

def json_response(x):
    return HttpResponse(json.dumps(x, sort_keys=True, indent=2, cls=DjangoJSONEncoder),
                        content_type='application/json; charset=UTF-8')


def ujson_response(x):
    return HttpResponse(ujson.dumps(x), content_type='application/json; charset=UTF-8')


def json_mongo(x):
    # return json.dumps(x, sort_keys=True, indent=2, cls=MongoEncoder)
    return json.dumps(x, sort_keys=True, indent=2, default=json_util.default)

def json_mongo_response(x):
    return HttpResponse(json_mongo(x), content_type='application/json; charset=UTF-8')


def json_errors(form):
    errors = []
    for k, v in form.errors.items():
        errors.append([k, unicode(v[0])])
    return errors, form.non_field_errors()
