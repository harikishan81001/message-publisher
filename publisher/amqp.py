import collections
import logging
import pika
import urlparse

from django.conf import settings


class RabbitMQBackend(object):
    """
    Backend class for handling RabbitMQ protocol
    """
    def open(self):
        url_str = settings.CLOUDAMQP_URL
        if settings.CLOUDAMQP_URL:
            url = urlparse.urlparse(url_str)
            params = pika.ConnectionParameters(
                host=url.hostname,
                virtual_host=url.path[1:],
                credentials=pika.PlainCredentials(url.username, url.password)
            )
            params.socket_timeout = settings.SOCKET_TIMEOUT
            self.connection = pika.BlockingConnection(params)
        else:
            self.connection = pika.BlockingConnection()

        self.channel = self.connection.channel()

    def create_exchange(self, exchange_name, durable=True, type='topic'):
        self.channel.exchange_declare(
            exchange_name, type=type, durable=durable)

    def delete_exchange(self, channel_drn):
        self.channel.exchange_delete(channel_drn)

    def publish(self, queue_name, body=None, **kwargs):
        exchange = kwargs.get("exchange", "")
        if not body:
            raise InvalidMessageRejected(
                "No body provided to publish"
            )

        self.channel.basic_publish(
            exchange=exchange, routing_key=queue_name,
            body=body,
            properties=pika.BasicProperties(delivery_mode=2)
        )

    def create_queue(self, queue_name=None, durable=True, exclusive=True):
        if queue_name is None:
            result = self.channel.queue_declare(
                durable=durable,
                exclusive=exclusive
            )
        else:
            result = self.channel.queue_declare(
                queue_name,
                durable=durable,
                exclusive=exclusive
            )
        queue_name = result.method.queue
        return queue_name

    def queue_bind(self, exchange=None, queue=None, routing_key=None):
        self.channel.queue_bind(
            exchange=exchange,
            queue=queue,
            routing_key=routing_key
        )

    def basic_consume(self, callback, queue=None, no_ack=True):
        self.channel.basic_consume(
            callback, queue=queue,
            no_ack=no_ack
        )

    def start_consuming(self):
        self.channel.start_consuming()

    def close(self):
        self.connection.close()
