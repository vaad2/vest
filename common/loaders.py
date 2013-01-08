from django.template.base import TemplateDoesNotExist
from models import SiteTemplate, SiteTheme
from thread_locals import get_current_site
def load_template_source(template_name, template_dirs=None):
    site = get_current_site()
    try:
        site_theme = SiteTheme.objects.get(site = site)
    except BaseException, e:
        site_theme = None

    try:
        template = SiteTemplate.objects.get(name = template_name, state = True, site_theme = site_theme, site = site)
        return template.content, None
    except BaseException, e:
        pass

    raise TemplateDoesNotExist, 'Cant find template in DB - %s'
load_template_source.is_usable = True