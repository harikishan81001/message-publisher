from django.db import models
from django.conf import settings
from django.core import cache


class TemplateManager(models.Manager):
    """
    Manager to handle cache level object accessing
    """
    def __get_key(self, irn):
        return "%s-%s" % ("template", irn)

    def get_template(self, irn):
        """
        Get channel by IRN, if found in cache returns from cache
        else fetch from db

        :params irn: Unique Identy Resource Name
        :raises: Template.DoesNotExist/Template.MultipleObjectsReturns
        """
        key = self.__get_key(irn)
        template = cache.cache.get(key)
        if not template:
            template = self.get(irn=irn)
            cache.cache.set(
                key, template,
                settings.CACHE_DEFAULT_EXPIRY_TIME
            )
        return template

    def invalidate_cache(self, template):
        """
        Invalidate Template cache on save or delete of instance

        :params template: Template instance
        """
        key = self.__get_key(template.irn)
        return cache.cache.delete(key)
