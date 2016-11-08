import logging
import re

from publisher.models import Template
from publisher.exceptions import InvalidMessage
from publisher.app_settings import STATUS

logger = logging.getLogger(__name__)


class ValidateTemplate(object):
    """
    Template Validator
    """
    def validate(self, adapter):
        if not adapter.template_irn:
            raise Template.DoesNotExist(
                "Sorry, No template identity number provided!"
            )
        template = Template.objects.get_template(adapter.template_irn)
        adapter.template = template
        return True


class ValidateMessage(object):
    """
    Validate message
    """
    def get_template_keys(self, template):
        """
        Returns all possible dynamic parameters
        """
        message = template.message
        return re.findall(r"\{(\w+)\}", message)

    def validate(self, adapter):
        errors = list()
        replace_vars = {}
        keys = self.get_template_keys(adapter.template)
        if keys and not adapter.keys:
            raise InvalidMessage(
                "No keys provided for replacement on message"
                " dynamic varidables"
            )

        for key in keys:
            if key not in adapter.keys:
                errors.append(key)
                continue
            replace_vars[key] = adapter.keys[key]
        if errors:
            raise InvalidMessage("Keys %s are required" % ",".join(errors))
        adapter.message = adapter.template.message.format(**replace_vars)
        return True


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
