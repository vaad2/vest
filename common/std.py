import hashlib, trans
import socket, os, codecs
import urllib2, urlparse
from django.contrib import auth
from django.core.files.base import ContentFile
from uuid import uuid4
from django.template import TemplateDoesNotExist
from django.template.defaultfilters import slugify
from datetime import datetime
from django.template.loader import make_origin, find_template_loader
from django.utils.datastructures import SortedDict
from django.utils.importlib import import_module
import sys
import re


def file_put_contents(filename, data, utf=False):
    f = codecs.open(filename, "w", "utf-8-sig") if utf else open(filename, 'w')
    f.write(data)
    f.close()


def file_get_contents(url):
    if os.path.exists(url):
        return open(url, 'r').read()

    opener = urllib2.build_opener()
    content = opener.open(url).read()
    return content

#deprecated
def settings_context_get():
    return os.environ.get('SETTINGS_CONTEXT', 'REMOTE')

#deprecated
def settings_context_set(hosts):
    if socket.gethostname() in hosts:
        os.environ.setdefault('SETTINGS_CONTEXT', 'LOCAL')
    else:
        os.environ.setdefault('SETTINGS_CONTEXT', 'REMOTE')


def is_local_settings(hosts):
    return socket.gethostname() in hosts


def ex_upload_def_get(path, **kwargs):
    def upload_path_get(obj, sub_path):
        img_path = [path]
        if 'field' in kwargs:
            field = kwargs['field']
            if field == 'self':
                img_path.append(str(obj.pk))
            else:
                lst = field.split('.')
                if len(lst) == 1:
                    img_path.append(str(getattr(obj, field).pk))
                else:
                    img_path.append(str(getattr(getattr(obj, lst[0]), lst[1])))

        name, ext = os.path.splitext(sub_path)
        if 'name_gen' in kwargs:
            sub_path = '%s%s' % (str(uuid4()), ext)
        else:
            sub_path = '%s%s' % (slugify_ru(name), ext)

        img_path.append(sub_path)

        return '/'.join(img_path)

    return upload_path_get


def upload_def_get(path, **kwargs):
    def upload_path_get(obj, sub_path):
        img_path = [path]
        if 'field' in kwargs:
            field = kwargs['field']
            if field == 'self':
                img_path.append(str(obj.pk))
            else:
                lst = field.split('.')
                if len(lst) == 1:
                    img_path.append(str(getattr(obj, field).pk))
                else:
                    img_path.append(str(getattr(getattr(obj, lst[0]), lst[1])))

        name, ext = os.path.splitext(sub_path)
        if 'name_gen' in kwargs:
            sub_path = '%s%s' % (str(uuid4()), ext)
        else:
            sub_path = '%s%s' % (slugify_ru(name), ext)

        img_path.append(sub_path)

        return '/'.join(img_path)

    return upload_path_get


def upload_def_get_2(path, **kwargs):
    from django.conf import settings

    def upload_path_get(obj, sub_path):
        name, ext = os.path.splitext(sub_path)
        if 'name_gen' in kwargs:
            sub_path = '%s%s' % (str(uuid4()), ext)
        else:
            sub_path = '%s%s' % (slugify_ru(name), ext)
        field = kwargs['field']
        lst = field.split('.')
        if len(lst) == 1:
            spath = str((getattr(obj, field).pk))
        else:
            spath = str(getattr(getattr(obj, lst[0]), lst[1]))

        image_path = path % (spath, sub_path)
        dir = '%s/%s' % (settings.MEDIA_ROOT, os.path.dirname(image_path))
        if not os.path.exists(dir):
            os.makedirs(dir)
        return image_path

    return upload_path_get


def image_from_url_get(url):
    url_data = urlparse.urlparse(url)

    ext = os.path.splitext(url_data.path)[1]
    return ContentFile(urllib2.urlopen(url).read())


def image_from_url_get_2(url, name_gen=True):
    file = image_from_url_get(url)
    ext = os.path.splitext(url)[1]
    if name_gen:
        md5 = hashlib.md5()
        md5.update('%s-%s' % (url, datetime.now()))
        if not ext:
            ext = '.jpg'

        file.name = '%s%s' % (md5.hexdigest(), ext)
    else:
        file.name = os.path.basename(url)

    return file


def slugify_ru(str):
    return slugify(str.encode('trans'))


def md5_for_file(f, block_size=2 ** 20):
    f = open(f)
    md5 = hashlib.md5()
    while True:
        data = f.read(block_size)
        if not data:
            break
        md5.update(data)

    f.close()
    return md5


def model_class_get(path):
    from django.db.models import get_model

    arr = path.split('.')
    return get_model(arr[0], arr[1])


def model_object_get(path, pk):
    cls = model_class_get(path)
    return cls.objects.get(pk=pk)


def class_get(path):
    arr = path.split('.')
    return getattr(import_module('.'.join(arr[0:-1])), arr[-1])


def qset_to_dict(qset, key='id'):
    res = SortedDict()
    for item in qset:
        res[getattr(item, key)] = item
    return res


def shop_login(request, username, password):
    if request.session.has_key(auth.SESSION_KEY):
        del request.session[auth.SESSION_KEY]
        request.session.modified = True

    user = auth.authenticate(username=username, password=password)
    if user is not None and user.is_active:
        auth.login(request, user)
    return user


def exception_details():
    exc_type, exc_obj, exc_tb = sys.exc_info()
    file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
    return file_name, exc_type, exc_obj, exc_tb


def dict_sort(dic_or_list, key):
    if isinstance(dic_or_list, list):
        sorted_x = sorted(dic_or_list, key=lambda x: x[key])
    else:
        sorted_x = sorted(dic_or_list.iteritems(), key=lambda x: x[1][key])
    return sorted_x


def handle_uploaded_file(f, path):
    destination = open(path, 'wb+')
    for chunk in f.chunks():
        destination.write(chunk)
    destination.close()


def ex_find_template(name, exclude=[], dirs=None):
    # Calculate template_source_loaders the first time the function is executed
    # because putting this logic in the module-level namespace may cause
    # circular import errors. See Django ticket #1292.
    template_source_loaders = None
    from django.conf import settings

    loaders = []
    for loader_name in settings.TEMPLATE_LOADERS:
        if loader_name in exclude: continue
        loader = find_template_loader(loader_name)
        if loader is not None:
            loaders.append(loader)
    template_source_loaders = tuple(loaders)
    for loader in template_source_loaders:
        try:
            return loader.load_template_source(name, dirs)
        except TemplateDoesNotExist:
            pass
    raise TemplateDoesNotExist(name)


def file_exists(path):
    try:
        with open(path) as f:
            return True
    except IOError as e:
        return None


def template_to_source():
    import codecs
    from django.conf import settings
    from django.template.loaders.app_directories import Loader
    from common.models import SiteTemplate

    loader = Loader()

    apps_root = os.path.realpath('%s/../' % settings.PROJECT_ROOT)

    for st in SiteTemplate.objects.all():
        for filepath in loader.get_template_sources(st.name):
            try:
                if file_exists(filepath) and filepath.startswith(apps_root):
                    with codecs.open(filepath, 'w', 'utf8') as f:
                        f.write(st.content)
                        print st.name, filepath, '-ok'
            except IOError as e:
                pass


first_cap_re = re.compile('(.)([A-Z][a-z]+)')
all_cap_re = re.compile('([a-z0-9])([A-Z])')


def camel_to_underline(name):
    s1 = first_cap_re.sub(r'\1_\2', name)
    return all_cap_re.sub(r'\1_\2', s1).lower()


class SiteMapGenerator(object):
    def _write_header(self):
        self.file.write('''<?xml version="1.0" encoding="UTF-8"?>''')

    def _open_urlset(self):
        self.file.write('''<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">''')

    def _close_urlset(self):
        self.file.write('</urlset>')

    def _write_urls(self, urls):
        for url in urls:
            self.file.write('<url>')
            self.file.write('<loc>%(loc)s</loc>' % url)
            self.file.write('<changefreq>%(changefreq)s</changefreq>' % url)
            self.file.write('<priority>%(priority)s</priority>' % url)
            self.file.write('</url>')

    def generate(self, path, **kwargs):
        try:
            self.file = open(path, 'w+')
            self._write_header()
            self._open_urlset()
            self._write_urls(kwargs['urls'])
            self._close_urlset()

        except BaseException, e:
            from common.std import exception_details

            import logging

            log = logging.getLogger('file_logger')
            ed = unicode(exception_details())
            log.log(logging.DEBUG, ed)

            return {'success': False, 'error': ed}
        finally:
            self.file.close()
        return {'success': True}

        #<?xml version="1.0" encoding="UTF-8"?>
        #<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
        #{% for item in items %}
        #{% if item.url|first == '/' %}
        #<url>
        #<loc>{{ item.url }}</loc>
        #<changefreq>weekly</changefreq>
        #<priority>1</priority>
        #</url>
        #{% endif %}
        #{% endfor %}
        #</urlset>