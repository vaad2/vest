from django import template
from django.template.base import Template
from django.template.context import Context
from django.template.loader import render_to_string
from django.template import Library, Node, TemplateSyntaxError
from django.template.loaders.filesystem import Loader
from common.consts import VEST_CURRENT_TREE
from common.thread_locals import get_thread_var

register = Library()

@register.tag(name = 'tag_simple_page')
def tag_simple_page(parser, token):
    args = token.split_contents()
    la = len(args)
    template_name = 'tag_simple_page.html'
    position_nav_mask = 15
    position_content_mask = 15
    extra_pos = 0

    if la > 1:
        position_content_mask = args[1]
    if la > 2:
        position_nav_mask = args[2]
    if la > 3 and len(args[3]) > 0:
        template_name = args[3]
    if la > 4:
        extra_pos = args[4]

    return TagSimplePageNode(position_content_mask, position_nav_mask, template_name, extra_pos)


class TagSimplePageNode(template.Node):
    def __init__(self, position_content_mask, position_nav_mask, template_name, extra_pos):
        self.position_nav_mask = int(position_nav_mask)
        self.position_content_mask = int(position_content_mask)
        self.template_name = template_name
        self.extra_pos = extra_pos

    def render(self, context):

        request = context['request']
        sps = []

        if hasattr(request, 'simple_page') and request.simple_page:
            for sp in request.simple_page:
                if sp.position_nav & self.position_nav_mask > 0 and sp.position_content & self.position_content_mask > 0 and sp.extra_pos == self.extra_pos :
                    if sp.is_content_template:
                        t = Template(sp.content)
                        c = Context({ 'request' : request })
                        sp.content = t.render(c)

                    sps.append(sp)

        return render_to_string(self.template_name,{ 'sps':sps })

@register.filter
def xrange_get(value, start = 0):
    if value:
        return xrange(start, value)
    return []

@register.filter
def int_get(value):
    try:
        return int(value)
    except BaseException, e:
        return 0

@register.filter
def inc_get(value, add = 1):
    return value + add


@register.simple_tag(takes_context = True)
def tag_curr_cat(context, name, attr, *args, **kwargs):
    cats = get_thread_var(VEST_CURRENT_TREE, None)
    if cats and name in cats:
        return getattr(cats[name], attr, '')
    return ''


@register.tag(name='include_raw')
def include_raw(parser, token):
    """
    Performs a template include without parsing the context, just dumps the template in.
    """
    bits = token.split_contents()
    if len(bits) != 2:
        raise TemplateSyntaxError, "%r tag takes one argument: the name of the template to be included" % bits[0]

    template_name = bits[1]
    if template_name[0] in ('"', "'") and template_name[-1] == template_name[0]:
        template_name = template_name[1:-1]

    source, path = Loader().load_template_source(template_name, None)
    return template.TextNode(source)
