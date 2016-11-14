# generic imports
import json
import sys
import logging
import pika

from requests import Request, Session

from django.conf import settings
from django.core.management.base import BaseCommand

from publisher.utils import get_backofftime
from publisher.amqp import RabbitMQBackend
from publisher.exceptions import AlreadyPublished
from publisher.app_settings import STATUS
from publisher.helpers import update_events_details
from publisher.helpers import get_req_status


logger = logging.getLogger(__name__)


def do_retry(channel, body):
    """
    Logic for publishing message to Deadletter Xchange
    where message will wait till TTL and after TTL expiration
    message will be forwarded to actual exchange
    """
    retries = body.get("retries", 0)
    grace_period = get_backofftime(retries + 1)
    body["maxretries"] = body["maxretries"] - 1
    body["retries"] = retries + 1

    retry_exchange = "DLX-%s" % grace_period
    retry_queue = "DLQ-%s" % grace_period

    properties = {
        "x-dead-letter-exchange": settings.CALLBACK_EXCHANGE,
        "x-message-ttl": grace_period,
        "x-dead-letter-routing-key": settings.CALLBACK_QUEUE
    }
    channel.exchange_declare(retry_exchange, "direct")
    channel.queue_declare(
        retry_queue,
        passive=False,
        durable=False,
        arguments=properties
    )
    channel.queue_bind(
        queue=retry_queue,
        exchange=retry_exchange,
        routing_key=retry_queue
    )
    channel.basic_publish(
        exchange=retry_exchange,
        routing_key=retry_queue,
        body=json.dumps(body),
        properties=pika.BasicProperties(delivery_mode=2)
    )


def callback(ch, method, properties, body):
    """
    Callback method to consume messages from shared queue

    :params ch: channel name
    :params method: method name
    :params properties: channel level properties
    :params body: consumed message body
    """
    print "[X] Received message %s" % body
    s = Session()
    if ch.is_closed:
        backend = RabbitMQBackend()
        backend.open()
        channel = backend.channel
    else:
        channel = ch

    try:
        body = json.loads(body)
        req_id = body['request_id']
        req_status = get_req_status(req_id)

        if req_status == STATUS.DLV:
            raise AlreadyPublished(
                "Message status for request id is alread delivered"
            )

        status = body['status']
        callback_details = body['callback']
        max_retries = body["maxretries"]
        http_method = callback_details["method"]

        url = callback_details["url"]
        headers = callback_details.get("headers", dict())
        params = callback_details.get("params", dict())
        req = Request(
            http_method, url,
            data=json.dumps({"status": status, "request_id": req_id}),
            headers=headers
        )
        req = req.prepare()
        resp = s.send(req, timeout=settings.REQ_TIMEOUT, verify=False)
        resp.raise_for_status()
    except KeyError as e:
        logger.error(
            "Important key %s missing,"
            " message can not be processed"
        )
    except AlreadyPublished:
        logger.info("No need to send message status")
    except Exception as e:
        if body["maxretries"] <= 0:
            logger.exception(
                "Sorry! message can not be processed,"
                " MaxRetries exhausted"
            )
        else:
            do_retry(channel, body)
    finally:
        channel.basic_ack(delivery_tag=method.delivery_tag)


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
        exchange = settings.CALLBACK_EXCHANGE
        queue = settings.CALLBACK_QUEUE

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
