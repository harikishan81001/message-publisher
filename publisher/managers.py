from django.db import models
from django.conf import settings
from django.core import cache


class ChannelManager(models.Manager):
    """
    Manager to handle cache level object accessing
    """
    def __get_key(self, irn):
        return "%s-%s" % ("channel", irn)

    def get_channel(self, irn):
        """
        Get channel by IRN, if found in cache returns from cache
        else fetch from db

        :params irn: Unique Identy Resource Name
        :raises: Channel.DoesNotExist/Channel.MultipleObjectsReturns
        """
        key = self.__get_key(irn)
        channel = cache.cache.get(key)
        if not channel:
            channel = self.get(irn=irn)
            cache.cache.set(
                key, channel,
                settings.CACHE_DEFAULT_EXPIRY_TIME
            )
        return channel

    def invalidate_cache(self, channel):
        """
        Invalidate channel cache on save or delete of instance

        :params channel: channel instance
        """
        key = self.__get_key(channel.irn)
        return cache.cache.delete(key)
