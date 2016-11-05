import copy
import json

from publisher.app_settings import STATUS
from publisher.amqp import RabbitMQBackend


class EventPublishStrategy(object):
    """
    strategy class for publishing events
    """
    def __init__(self, request_id, strategy, message, **kwargs):
        """
        initialize publisher class with strategy

        :params request_id: unique request id
        :strategy: strategy class
        """
        self.validations = []
        self.strategy = strategy
        self.request_id = strategy
        self.message = message
        self.channel = kwargs.get("channel", None)

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
                    on_exception(self, exabbitMQBackendUS.REJ)
            return wrap

        for validation in validations:
            _klass = validation()
            self.validations.append(_wrapper(_klass.validate))
        return self

    def while_processing_do(
            self, on_exception=lambda self, exc: None,
            when_done=lambda obj, msg: None):
        """
        bind methods calls with multiple actions
        """
        _klass = self.strategy(self.request_id)

        def _wrapper():
            """
            wrapper which process execution of methods
            """
            message = ""
            try:
                message = _klass.publish()
            except Exception as exc:
                on_exception(self, exc)
            else:
                when_done(self, message)
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

        for _func in self.also_do_fn:
            _func(self)
        return response


class Strategy(object):
    """
    Publishing strategy
    """
    def __init__(self, adapter, request_id):
        self.request_id = request_id
        self.adapter = adapter

    def get_payload(self):
        payload = copy.deepcopy(self.adapter.message)
        payload.update(request_id=request)
        return payload

    def publish(self):
        exchange = settings.PUBLISH_EXCHANGE
        queue = settings.PUBLISH_QUEUE.format(
            env=settings.ENV
        )
        backend = RabbitMQBackend()
        backend.open()
        payload = self.get_payload()
        return backend.publish(
            queue, body=json.dumps(body),
            exchange=exchange
        )
