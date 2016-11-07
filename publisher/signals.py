from django.core import cache
from django.db.models.signals import post_save, pre_delete

from publisher.models import Template


def expire_template_cache(sender, **kwargs):
    """
    Utility method to expire signal cache
    """
    instance = kwargs["instance"]
    return sender.objects.invalidate_cache(instance)


post_save.connect(expire_template_cache, sender=Template)
pre_delete.connect(expire_template_cache, sender=Template)
