import inspect, json
from django.conf.urls.defaults import include, url, patterns
from django.utils.importlib import import_module
from common.views import MixinBase

from django.views.generic import View
from django.http import HttpResponse


def ajax_urlpatterns():
    from django.conf import settings

    urlpatterns = []
    urls = {
        'link_view': {},
        'view_link': {}
    }

    verbs = {'View': 'view', 'Crea': 'create', 'Upda': 'update', 'Dele': 'delete'}
    for app in settings.INSTALLED_APPS:
        import_module(app)
        try:
            urls_list = []
            module = import_module('%s.ajax_views' % app)
            for name, obj in inspect.getmembers(module, inspect.isclass):
                if issubclass(obj, MixinBase):
                    if name[:4] in verbs:
                        view_name = name
                        full_view_name = '%s:%s' % (app, view_name)

                        verb = verbs[name[:4]]
                        link = '/ajax/%s/%s/%s/' % (app, verb, view_name[len(verb):].lower())

                        urls['link_view'][link] = full_view_name
                        urls['view_link'][full_view_name] = link

                        urls_list.append(url(r'^%s$' % link[6:], obj.as_view(), name=view_name))
            if len(urls_list):
                urlpatterns += patterns(r'',
                                        url(r'ajax/', include(patterns('', *urls_list), namespace='ajax_%s' % app)))
        except BaseException, e:
            pass

    class ViewDynamicUrls(View):
        def dispatch(self, request, *args, **kwargs):
            return HttpResponse('var g_urls=%s;' % json.dumps(urls, separators=(',', ':')), mimetype='text/javascript')

    urlpatterns += patterns(r'', url(r'^dynamic/js/urls.js$', ViewDynamicUrls.as_view(), name='view_dynamic_urls'))

    return urlpatterns
