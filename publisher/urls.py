from django.conf.urls import patterns, include, url

from publisher.apiviews import PublishAPI


urlpatterns = [
    url(
        r'publish/events/',
        PublishAPI.as_view(), name='publish_api'
    ),
    url(
        r'^api-auth/', include('rest_framework.urls',
        namespace='rest_framework')
    )
]
