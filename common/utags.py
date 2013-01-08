from django.template.loader import render_to_string
import re
from django import forms
from django.db.models import Q
from common.std import model_class_get
from  consts import *
from common.thread_locals import get_thread_var, set_thread_var

def utag_form(context, form_class, *args, **kwargs):
    template_name = kwargs.get('template_name', 'tag_form.html')
    template_name_success = kwargs.get('template_name_success', 'tag_form_success.html')

    request = context['request']
    form_name = request.REQUEST.get('_form_name', None)


    if form_name == form_class.__name__.lower():
        form = form_class(request.POST or None)
        if request.method == 'POST' and form.is_valid():
            if 'handler_is_valid' in kwargs:
                kwargs['handler_is_valid'](request, form)

            if 'handler_success' in kwargs:
                kwargs['handler_success'](request, form)

            return render_to_string(template_name_success, { 'form' : form })

        return render_to_string(template_name, { 'form' : form })

    return render_to_string(template_name, { 'form' : form_class() })

def utag_tree(context, *args, **kwargs):
    template_name = kwargs.get('template_name', 'tag_tree.html')
    request = context['request']
    url = re.sub(r'/+', '/', '/%s/' % request.path_info.strip('/'), re.IGNORECASE)
    max_level = kwargs.get('max_level', 100)

    qkwargs = kwargs.get('qkwargs', {})
    cls = kwargs['cls']
    cats = get_thread_var(VEST_CURRENT_TREE, {})
    if isinstance(cls, basestring):
        cls = model_class_get(cls)
    try:
        item = cls.objects.get(pk = args[0])
    except BaseException, e:
        item = cls.objects.get(name = args[0])

    items = list(item.descendants_get(qkwargs))

    if 'cmp' in kwargs:
        cmp = kwargs['cmp']
    else:
        def cmp(op1, item):
            return op1 == item.url

    if len(items):
        active_item = None
        prev_item = None
        item_map = {}
        for item in items:
            if item.level > max_level:
                continue
            if prev_item and prev_item.level < item.level:
                prev_item.open = True

            if prev_item and prev_item.level > item.level:
                prev_item.close = prev_item.level - item.level
            else:
                item.close = 0

            prev_item = item
            item_map[str(item.pk)] = item

            if cmp(url, item):
                cats[args[0]] = item
                active_item = item
                item.active = True
                item.current = True

        item.close = item.level - items[0].level
        if active_item:
            for item_pk in active_item.path.split(','):
                if item_pk in item_map:
                    item_map[item_pk].active = True

    set_thread_var(VEST_CURRENT_TREE, cats)

    return render_to_string(template_name, {
        'items': items,
        'curr_url': url,
        'request': request,
        'args' : args,
        'kwargs' :kwargs
    })

