import redis

from redisco import models

from django.conf import settings


connection_pool = redis.ConnectionPool(
    host=settings.REDISCO_REDIS_HOST,
    port=settings.REDISCO_REDIS_PORT,
    db=settings.REDISCO_REDIS_DB
)


class EventsDetails(models.Model):
    """
    Count against protocols
    """
    template_id = models.Attribute(required=True)
    status = models.Attribute(required=True)
    request_id = models.Attribute()

    @property
    def db(cls):
        return redis.Redis(
            connection_pool=connection_pool
        )
