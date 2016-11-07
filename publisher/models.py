from __future__ import unicode_literals

from django.db import models
from django.core.validators import validate_slug

from jsonfield import JSONField

from publisher.utils import get_default_policy
from publisher.managers import TemplateManager


class Template(models.Model):
    """
    Model to store channel's low level details
    """
    name = models.CharField(
        max_length=100, help_text="Channel Name !"
    )
    irn = models.CharField(
        max_length=20,
        validators=[validate_slug],
        unique=True,
        help_text="Identity Resource Name(Unique) !"
    )
    policy = JSONField(
        default=get_default_policy(),
        help_text="Configurable channel policy !"
    )
    message = models.TextField(
        help_text=(
            "Message Template,"
            " Dynamic parameters can be configured like"
            " Hi {user}, your {shipment} will be delivered on"
            " {date}"
        )
    )

    objects = TemplateManager()

    def __unicode__(self):
        return "%s(%s)" % (self.name, self.irn)
