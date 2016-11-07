import logging

from publisher.models import Template
from publisher.exceptions import InvalidMessage
from publisher.utils import get_default_message_format


logger = logging.getLogger(__name__)


class ValidateTemplate(object):
    """
    Template Validator
    """
    def validate(self, adapter):
        if not adapter.template:
            raise Template.DoesNotExist(
                "Sorry, No template identity number provided!"
            )
        channel = Template.objects.get_channel(adapter.template)
        adapter.template = template


class ValidateMessage(object):
    """
    Validate message
    """
    def validate(self, adapter):
        default_schema = get_default_message_format()
        if not adapter.message:
            raise InvalidMessage(
                "No message provided for publishing"
            )
        errors = list()
        for key, conf in default_schema:
            required, default = (
                conf.get("required", False),
                conf.get("default")
            )
            if required:
                if not conf.get(key):
                    errors.append(
                        "{key} is mandatory !".format(key=key)
                    )

            else:
                if not conf.get(key):
                    message.update(**{key:default})
        if errors:
            raise InvalidMessage(",".join(errors))


def log_message(publisher, status=STATUS.FAIL, exc=None):
    """
    logs event in logging system with details
    """
    if exc:
        message = (
            "%s to process event"
            " exception=%s, status=%s" % (
                status, exc.__repr__(), status
            )
        )
    else:
        message = "Message sent to queue %s" % status
    logger.info(message)
