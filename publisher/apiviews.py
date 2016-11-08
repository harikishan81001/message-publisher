from __future__ import absolute_import

from uuid import uuid4
import json

from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework import status
from rest_framework.response import Response

from publisher.strategy import EventPublishStrategy, Strategy
from publisher.helpers import ValidateTemplate, ValidateMessage
from publisher.helpers import ValidateMessageStatus
from publisher.helpers import log_message
from publisher.app_settings import STATUS


class PublishAPI(APIView):
    """
    API endpoint for publishing messages
    """
    http_method_names = ['post']
    authentication_classes = (TokenAuthentication,)

    def get_request_id(self):
        return uuid4().hex

    def post(self, request):
        """
        HTTP POST method request handler
        """
        req_status = STATUS.REJ
        request_id = self.get_request_id()
        keys = request.data.get("keys", {})

        # configuire publisher
        publisher = EventPublishStrategy(
            Strategy,
            request_id,
            keys,
            request.data.get("template_irn"),
        )

        # before processing let's do some validations
        publisher.before_processing(
            validations=[
                ValidateTemplate,
                ValidateMessage,
                ValidateMessageStatus
            ],
            on_exception=log_message
        )

        # let's prcess event now as everything is validated and all ok
        if publisher.is_valid():
            publisher.while_processing_do(
                on_exception=log_message,
                when_done=log_message
            )
            message = publisher.run()
            req_status = STATUS.QUE
        return Response(
            json.dumps(
                {"status": req_status, "request_id": request_id}
            ), status=status.HTTP_202_ACCEPTED)
