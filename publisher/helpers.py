from publisher.models import Channel
from publisher.exceptions import InvalidMessage
from publisher.utils import get_default_message_format


class ValidateChannel(object):
    """
    Channel Validator
    """
    def validate(self, adapter):
        if not adapter.channel:
            raise Channel.DoesNotExist(
                "Sorry, No channel identity number provided!"
            )
        channel = Channel.objects.get_channel(adapter.channel)
        adapter.channel = channel


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
