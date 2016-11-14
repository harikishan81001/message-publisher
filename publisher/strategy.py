import copy
import json

from django.conf import settings

from publisher.app_settings import STATUS
from publisher.amqp import RabbitMQBackend

from publisher.helpers import index_events_details


class EventPublishStrategy(object):
    """
    strategy class for publishing events
    """
    def __init__(self, strategy, request_id, keys, template, callback):
        """
        initialize publisher class with strategy

        :params request_id: unique request id
        :strategy: strategy class
        """
        self.validations = []
        self.strategy = strategy
        self.request_id = request_id
        self.message = None
        self.template = None
        self.template_irn = template
        self.keys = keys
        self.callback_info = callback

    def before_processing(
            self, validations=None,
            on_exception=lambda self, exc: None):
        """
        attach validators to process validations

        :params validations: list of validation classes
         which will be executed in sequence
        :params on_exception: if validation fails exception is raises
         so exception trapper to trap the exception and do proper action
        """
        def _wrapper(_method):
            """
            wrapper which process execution of methods
            """
            def wrap(self):
                try:
                    return _method(self)
                except Exception as exc:
                    on_exception(self, status=STATUS.REJ, exc=exc)
                    return False
            return wrap

        for validation in validations:
            _klass = validation()
            self.validations.append(_wrapper(_klass.validate))
        return self

    def while_processing_do(
            self, on_exception=lambda self, status, exc: None,
            when_done=lambda obj, status, exc: None):
        """
        bind methods calls with multiple actions
        """
        _klass = self.strategy(self, self.request_id)

        def _wrapper():
            """
            wrapper which process execution of methods
            """
            message = ""
            try:
                message = _klass.publish()
            except Exception as exc:
                on_exception(self, STATUS.FAIL, exc)
            else:
                index_events_details(
                    self.request_id, self.template_irn, STATUS.QUE,
                )
                when_done(self, STATUS.QUE, None)
            return message

        self.trigger = _wrapper
        return self

    def run(self):
        """
        trigger method to trigger the process
        """
        def trigger():
            _klass = self.strategy(self, self.request_id)
            return _klass.publish()

        if not self.trigger:
            self.trigger = trigger

        response = self.trigger()
        return response

    def is_valid(self):
        """
        actual invoking method for validations
        """
        is_valid = True
        for validation in self.validations:
            is_valid = validation(self)

            # break further execution if any validation fails
            if not is_valid:
                break

        return is_valid


class Strategy(object):
    """
    Publishing strategy
    """
    def __init__(self, adapter, request_id):
        self.request_id = request_id
        self.adapter = adapter

    def get_payload(self):
        payload = dict()
        payload.update(
            request_id=self.request_id,
            message=self.adapter.message,
            url=self.adapter.template.url,
            method=self.adapter.template.method,
            headers=self.adapter.template.headers,
            template_irn=self.adapter.template.irn,
            maxretries=self.adapter.template.policy.get("maxRetries", 3),
            callback=self.adapter.callback_info
        )
        return payload

    def publish(self):
        exchange = settings.PUBLISH_EXCHANGE
        queue = settings.PUBLISH_QUEUE
        backend = RabbitMQBackend()
        backend.open()
        payload = self.get_payload()
        return backend.publish(
            queue, body=json.dumps(payload),
            exchange=exchange
        )
