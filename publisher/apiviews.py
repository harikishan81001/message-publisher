from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework import status

from publisher.strategy import EventPublishStrategy, Strategy
from publisher.helpers import ValidateTemplate, ValidateMessage
from publisher.helpers import log_message


class PublishAPI(APIView):
    """
    API endpoint for publishing messages
    """
    http_method_names = ['post']

    def post(self, request):
        """
        HTTP POST method request handler
        """
        # configuire publisher
        publisher = EventPublishStrategy(
            Strategy, request_id, request.DATA
        )

        # before processing let's do some validations
        valid_for_publishing = publisher.before_processing(
            validations=[
                ValidateTemplate,
                ValidateMessage,
            ],
            on_exception=log_message
        ).do_validate(also_do_if_valid=log_message)

        # let's prcess event now as everything if all ok
        if valid_for_publishing:
            publisher.while_processing_do(
                on_exception=log_message,
                when_done=log_message
            )
            message = publisher.run()
