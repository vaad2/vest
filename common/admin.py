import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "proff.settings")

from django.contrib.admin.sites import AdminSite
from django.utils.importlib import import_module

import logging
logger = logging.getLogger('proff')


class SuperAdminSite(AdminSite):
    def has_permission(self, request):
        return request.user.is_superuser and request.user.is_active and request.user.is_staff


def autodiscover(admin_super, **kwargs):
    from django.conf import settings
    for app in settings.INSTALLED_APPS:
        try:
            module = import_module('.admin', app)
            try:
                module.admin_register(admin_super)
                print 'fn ok'
            except AttributeError:
                logger.debug('cant import fn')

        except BaseException, e:
            logger.debug('cant find admin module %s' % app)

