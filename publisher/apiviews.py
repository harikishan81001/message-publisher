from rest_framework.views import APIView
from rest_framework.authentication import TokenAuthentication
from rest_framework.renderers import JSONRenderer
from rest_framework import status


class PublishAPI(APIView):
    """
    API endpoint for publishing messages
    """
    http_method_names = ['post']

    def post(self, request):
        """
        HTTP POST method request handler
        """
        pass
