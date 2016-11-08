# generic imports
import json
import sys
import logging

import concurrent.futures
import urllib.request

from django.conf import settings
from django.core.management.base import BaseCommand

from publisher.amqp import RabbitMQBackend


logger = logging.getLogger(__name__)


def make_call(url, method, message, headers):
    res = urllib.request.urlopen(url, timeout=settings.request_timeout) as conn:



def callback(ch, method, properties, body):
    """
    Callback method to consume messages from shared queue

    :params ch: channel name
    :params method: method name
    :params properties: channel level properties
    :params body: consumed message body
    """
    print ch, method, properties, body
    pass


class Command(BaseCommand):
    """
    Worker management command
    """
    help = 'Command to start consumers'

    PREFETCH_COUNT = 100

    def handle(self, *args, **options):
        """
        Command handler
        """
        exchange = settings.PUBLISH_EXCHANGE
        queue = settings.PUBLISH_QUEUE
        backend = RabbitMQBackend()
        backend.open()
        try:
            backend.channel.basic_qos(prefetch_count=self.PREFETCH_COUNT)
            queue_name = backend.create_queue(
                queue, exclusive=False
            )
            backend.queue_bind(
                exchange=exchange,
                queue=queue,
                routing_key=queue
            )
            backend.basic_consume(callback, queue=queue, no_ack=False)
            logger.info("[X] Started worker pointing to %s-%s" % (
                exchange, queue)
            )
            backend.start_consuming()
        except Exception as e:
            logger.error(
                "Worker exited due to some critical error %s,"
                " please check !" % str(e)
            )
            raise e
        except KeyboardInterrupt as e:
            logger.info("[X] Got signal for quiting the program, quiting...")
            backend.close()
            sys.exit(0)
