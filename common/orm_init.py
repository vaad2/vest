import os
import shutil, random, types, codecs
from datetime import datetime
from django.db import connection
from django.contrib.auth.models import User
from django.core.files import File
from django.template.loader import render_to_string
import urllib2, os, hashlib

from django.conf import settings

def truncate(model):
    try:
        cursor = connection.cursor()
        cursor.execute("TRUNCATE TABLE `%s`" % model._meta.db_table)
    except Exception, e:
        print e

def upload_def_get(path, **kwargs):
    def upload_path_get(obj, sub_path):
        img_path = [ path ]

        if 'field' in kwargs:
            if kwargs['field'] == 'self':
                img_path.append(str(obj.pk))
            else:
                img_path.append(str(getattr(obj, kwargs['field']).pk))

        img_path.append(sub_path)

        return '/'.join(img_path)
    return upload_path_get

def upload_def_get_2(path, **kwargs):
    def upload_path_get(obj, sub_path):
        return path % (str(getattr(obj, kwargs['field']).pk), sub_path)

    return upload_path_get




def render_to_file(template, filename, context):
    codecs.open(filename, 'w', 'utf-8').write(render_to_string(template, context))

def wrap(method):
    def wrapper(self, *args, **kwargs):
        fun_bf = kwargs.get('_bf', None)
        fun_af = kwargs.get('_af', None)
        if '_bf' in kwargs:
            del kwargs['_bf']
        if '_af' in kwargs:
            del kwargs['_af']

        if fun_bf:
            fun_bf(self, *args, **kwargs)

        result = method(self, *args, **kwargs)

        if fun_af:
            fun_af(self, result, *args, **kwargs)

        return result
    return wrapper

def init_attributes(name, bases, dict):
    for key, item in dict.iteritems():
        if isinstance(item, types.FunctionType):
            dict[key] = wrap(item)

    return type(name, bases, dict)


class CommandMixin(object):
    __metaclass__ = init_attributes

    def handle(self, *args, **options):
        if len(args) and args[0] == 'clear':
            migrate = []
            import MySQLdb
            if 'migrate' in options:
                migrate = options['migrate']
                del options['migrate']

            db = MySQLdb.connect(user = 'root', passwd = 'root')
            cursor = db.cursor()
            db_name = settings.DATABASES['default']['NAME']
            try:
                cursor.execute('DROP DATABASE IF EXISTS `%s`' % db_name)
            except Exception, e:
                print e

            cursor.execute('CREATE DATABASE `%s` CHARACTER SET utf8 COLLATE utf8_general_ci' % db_name)

            from south.management.commands.migrate import Migrations
            from django.core import management
            from django.db import transaction


            for app in migrate:
                path = '%s/%s/migrations' % (settings.ROOT_PATH, app)
                try:
                    shutil.rmtree(path)
                except Exception, e:
                    print e

#                if not os.path.exists(path):
#                    os.makedirs(path)
#                    open('%s/__init__.py' % path,'w').close()

            Migrations.instances = {}
            management.call_command('syncdb', interactive = 0)
            try:
                management.call_command('loaddata', 'fixtures/initial_data.json')
            except Exception, e:
                print e


            for app in migrate:
                management.call_command('schemamigration', app, initial = True, interactive = 0)
                Migrations.instances = {}
                management.call_command('migrate', app, fake = True, interactive = 0)

#            management.call_command('migrate', interactive = 0)


    def rand_str(self, str):
        return str % random.randint(1, 80000000)

    def user_create(self, password, **kwargs):
        now = datetime.now()
        id = int(User.objects.all().order_by('-id')[0].pk) + 1
        kwargs['username'] = kwargs.get('username', 'username%s' % id)
        kwargs['email'] = kwargs.get('email', 'email%s@test.ru' % id)
        kwargs['is_staff'] = kwargs.get('is_staff', False)
        kwargs['is_active'] = kwargs.get('is_active', True)
        kwargs['is_superuser'] = kwargs.get('is_superuser', False)
        kwargs['last_login'] = kwargs.get('last_login', now)
        kwargs['date_joined'] = kwargs.get('date_joined', now)


        user = User(**kwargs)
        user.set_password(password)
        user.save()

        return user

    def rnd_md(self, model):
        return model.objects.order_by('?')


    def truncate(self, model):
        truncate(model)
#        try:
#            cursor = connection.cursor()
#            cursor.execute("TRUNCATE TABLE `%s`" % model._meta.db_table)
#        except Exception, e:
#            print e

    def auto_inc_set(self, model, val):
        from django.db import connection
        cursor = connection.cursor()
        cursor.execute("ALTER TABLE `%s` AUTO_INCREMENT = %s" % (model._meta.db_table, val))

    def media_del(self, path):
        if os.path.exists('%s/%s' % (settings.MEDIA_ROOT, path)):
            try:
                shutil.rmtree('%s/%s' % (settings.MEDIA_ROOT, path))
            except Exception, e:
                print e

    def media_create(self, path):
        path = '%s/%s' % (settings.MEDIA_ROOT, path)
        if not os.path.exists(path):
            os.makedirs(path)

    def media_init(self, path):
        self.media_del(path)
        self.media_create(path)

    def image_save(self, image, i):
        file = open('%s/static/img/assets/%s.jpg' % (settings.ROOT_PATH, i), 'rb')
        image.save('img%s.jpg' % i, File(file))
        file.close()

    def data_gen(self, model, start = 1, stop = 10, commit = True, **kwargs):
        data_cnt = 0
        data_len = 0

        if isinstance(kwargs['data'], list):
            data_len = len(kwargs['data'])

        for i in xrange(start, stop):
            if data_len:
                data = kwargs['data'][data_cnt]
            else:
                data = kwargs['data']

            params = dict(data)
            for key in params.iterkeys():
                try:
                    if isinstance(params[key], str):
                        params[key] = params[key] % i
                    if isinstance(params[key], types.FunctionType) or (params[key].im_self is not None):
                        params[key] = params[key](key)

                except Exception, e:
                    pass
            try:
                if commit:
                    obj = model.objects.create(**params)
                else:
                    obj = model(**params)
            except Exception, e:
                print Exception, e
                yield None

            if 'image' in kwargs and commit:
                self.image_save(getattr(obj, kwargs['image']), i)

            data_cnt += 1
            if data_cnt >= data_len:
                data_cnt = 0

            yield obj

def win_correct_file_name(filename):
    import win32api
    return win32api.GetLongPathName(win32api.GetShortPathName(filename))
