from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import resolve
from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.template.response import TemplateResponse
from django.views.generic.base import TemplateView, View
from django.views.generic.list import MultipleObjectMixin
from common.decorators import json_handler_decorator_dispatch
from common.http import json_response, json_mongo_response
from common.std import camel_to_underline
from models import SiteSettings
from django.db.models.query import QuerySet
from django.utils.safestring import mark_safe
import math, json, urllib
from django.utils.encoding import smart_str


class ViewDefault(TemplateView):
    template_name = 'base.html'

    def get_template_names(self):
        """
        Returns a list of template names to be used for the request. Must return
        a list. May not be called if render_to_response is overridden.
        """
        if hasattr(settings, 'SIMPLE_PAGE_TEMPLATE'):
            return [settings.SIMPLE_PAGE_TEMPLATE]

        if self.template_name is None:
            raise ImproperlyConfigured(
                "TemplateResponseMixin requires either a definition of "
                "'template_name' or an implementation of 'get_template_names()'")
        else:
            return [self.template_name]

    def post(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        sp = request.simple_page
        if sp:
            context = self.get_context_data(**kwargs)
            context['simple_page'] = sp[0]

            if sp[0].site_template:
                return render(request, sp[0].site_template.name, context)

            return self.render_to_response(context)
        raise Http404


class ViewRobots(View):
    def dispatch(self, request, *args, **kwargs):
        return HttpResponse(SiteSettings.robots_get(), mimetype='text/plain')

#need to check
class ExPaginator(object):
    def __init__(self,
                 num_rows,
                 offset=0,
                 limit=10,
                 view_num=11,
                 splitter='...',
                 view_one_page=False,
                 min_limit=10,
                 max_limit=50,
                 name_offset='offset',
                 name_limit='limit',
                 request=None,
                 map_page=None,
                 params=None):

        self.num_rows = num_rows

        if request:
            try:
                offset = int(request.REQUEST.get(name_offset, offset))
                limit = int(request.COOKIES.get(name_limit, limit))
            except Exception, exception:
                pass

        if limit < min_limit:
            limit = min_limit

        if limit > max_limit:
            limit = max_limit

        if offset > num_rows:
            offset = num_rows - limit

        self.num_rows = num_rows

        self.offset = offset
        self.limit = limit
        self.view_num = view_num
        self.splitter = splitter
        self.view_one_page = view_one_page
        self.num_pages = int(math.ceil(float(num_rows) / limit))
        self.curr_page = int(math.ceil(offset / limit))
        self.view_one_page = view_one_page

        if self.curr_page >= self.num_pages:
            self.curr_page = self.num_pages - 1

        self.next_page = self.curr_page + 1
        if self.next_page >= self.num_pages:
            self.next_page = self.num_pages - 1

        self.prev_page = self.curr_page - 1
        if self.prev_page < 0:
            self.prev_page = 0

        self.offset_next_page = limit * self.next_page
        self.offset_prev_page = limit * self.prev_page
        self.offset_last_page = limit * (self.num_pages - 1)

        self.curr_page += 1
        self.next_page += 1
        self.prev_page += 1

        self.name_offset = name_offset
        self.name_limit = name_limit
        self.map_page = map_page


        if params and self.name_offset in params:
            params = dict(params)
            del params[self.name_offset]

        self.params = params

        if self.params:
            self.params_json = ',%s' % json.dumps(self.params, sort_keys=True, indent=2)[1:-1]
            items = {}
            for key, val in self.params.iteritems():
                if isinstance(val, str) or isinstance(val, unicode):
                    items[key] = val.encode('utf-8')
                else:
                    items[key] = val
            self.params_urlencoded = urllib.urlencode(items)
        else:
            self.params_json, self.params_urlencoded = '', ''

        if self.map_page:
            if self.next_page in self.map_page:
                self.next_page_data = self.map_page[self.next_page]

            if self.prev_page in self.map_page:
                self.prev_page_data = self.map_page[self.prev_page]

        self.page_range = self._get_page_range()


    def _get_page_range(self):
        num_pages = self.num_pages
        splitter = {'is_splitter': True, 'splitter': self.splitter}
        view_num = self.view_num
        curr_page = self.curr_page
        limit = self.limit

        if num_pages <= view_num:
            pages = [[i, (i - 1) * limit] for i in xrange(1, num_pages + 1)]
            #pages = [[i, (i - 1) * num_page] for i in xrange(1, num_pages + 1)]
        else:
            df = self.view_num / 2
            pages = []
            if curr_page <= df:
                pages.extend([[i, (i - 1) * limit] for i in xrange(1, view_num)])
                pages.append(splitter)
            elif curr_page >= num_pages - df:
                pages.append([1, 0])
                pages.append(splitter)
                #pages.extend(range(num_pages - viewed_num + 2, num_pages ))

                pages.extend([[i, (i - 1) * limit] for i in xrange(num_pages - view_num + 2, num_pages)])

            else:
                pages.append([1, 0])
                if curr_page != df + 1:
                    pages.append(splitter)
                    #                pages.extend(range(curr_page - df + 1, curr_page + df))
                pages.extend([[i, (i - 1) * limit] for i in xrange(curr_page - df + 1, curr_page + df)])

                if curr_page != num_pages - df:
                    pages.append(splitter)

            pages.append([num_pages, (num_pages - 1) * limit])

        if self.map_page:
            for page in pages:
                if page[0] in self.map_page:
                    page.append(self.map_page[page[0]])

        return pages
        #    page_range = property(_get_page_range)


class ExMultipleObjectMixin(MultipleObjectMixin):
    view_num = 10
    query_params = {}

    def get_view_num(self):
        return self.view_num

    def get_context_object_name(self, object_list=None):
        """
        Get the name of the item to be used in the context.
        """
        if self.context_object_name:
            return self.context_object_name
        elif object_list and hasattr(object_list, 'model'):
            return smart_str('%s_list' % object_list.model._meta.object_name.lower())
        else:
            return 'object_list'

    def get_paginator(self, queryset, per_page, orphans=0, allow_empty_first_page=True, params=None):
        return ExPaginator(queryset.count(),
                           request=self.request,
                           max_limit=per_page,
                           limit=per_page,
                           view_num=self.get_view_num(),
                           splitter=mark_safe('<span>...</span>'),
                           params=params)

    def paginate_queryset(self, queryset, page_size, params=None):
    #        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty())
        paginator = self.get_paginator(queryset, page_size, allow_empty_first_page=self.get_allow_empty(),
                                       params=params)
        return paginator, None, queryset[paginator.offset: paginator.offset + paginator.limit], paginator.num_rows > 1

    def get_context_data(self, **kwargs):
        """
        Get the context for this view.
        """
        queryset = kwargs.pop('object_list')
        page_size = self.get_paginate_by(queryset)
        context_object_name = self.get_context_object_name(queryset)

        if page_size:
            if not len(self.query_params):
                self.query_params = dict(self.request.REQUEST)

            paginator, page, queryset, is_paginated = self.paginate_queryset(queryset, page_size,
                                                                             params=kwargs.get('params',
                                                                                               self.query_params))
            context = {
                'paginator': paginator,
                'page_obj': page,
                'is_paginated': is_paginated,
                context_object_name: queryset,
                'object_list': queryset
            }
        else:
            context = {
                'paginator': None,
                'page_obj': None,
                'is_paginated': False,
                context_object_name: queryset,
                'object_list': queryset
            }
        context.update(kwargs)
        context_object_name = self.get_context_object_name(queryset)
        if context_object_name is not None:
            context[context_object_name] = queryset
        return context


class MixinBase(View):
    breadcrumbs = []
    template_name_base = 'base.html'

    def get_breadcrumbs(self):
        return self.breadcrumbs

    def get_template_name_base(self):
        template_name_base = self.template_name_base
        if self.request.is_ajax():
            template_name_base = '%s_ajax.%s' % tuple(template_name_base.split('.'))
        return template_name_base

    def render_to_response(self, context, **response_kwargs):
        context.update({'breadcrumbs': self.get_breadcrumbs,
                        'template_name_base': self.get_template_name_base()})

        return self.response_class(
            request=self.request,
            template=self.get_template_names(),
            context=context,
            **response_kwargs
        )

    def get_template_names(self):

        if self.template_name:
            tn = self.template_name
        else:
            namespace = resolve(self.request.path).namespace
            base = camel_to_underline(self.__class__.__name__)
            tn = '%s/%s.html' % (namespace, base)

        if self.request.is_ajax():
            tna = tn.split('.')
            tna[-2] = '%s_ajax' % tna[-2]
            return ['.'.join(tna)]

        return [tn]


    def dispatch(self, request, *args, **kwargs):
        if 'pk' in request.REQUEST:
            kwargs['pk'] = request.REQUEST
        if 'slug' in request.REQUEST:
            kwargs['slug'] = request.REQUEST['slug']

        result = super(MixinBase, self).dispatch(request, *args, **kwargs)

        if request.is_ajax():
            if isinstance(result, TemplateResponse):
                if not result.is_rendered:
                    result.render()
                result = result.rendered_content
            if hasattr(self, 'ajax_errors') and len(self.ajax_errors):
                return json_mongo_response({'success': False, 'errors': self.ajax_errors})
            return json_mongo_response({'success': True, 'data': result})

        return result

class AjaxView(MixinBase):
    def post_process(self, result, request, *args, **kwargs):
        if not isinstance(result, HttpResponse):
            if isinstance(result, (list, tuple)):
                success, data = result
            else:
                success = result
                data = None
            return json_mongo_response({'success' : success, 'data' : data})
        return result
    @json_handler_decorator_dispatch(post_process=post_process)
    def dispatch(self, request, *args, **kwargs):
        return super(AjaxView, self).dispatch(request, *args, **kwargs)