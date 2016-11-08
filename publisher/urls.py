from django.conf.urls import include, url

from publisher.apiviews import PublishAPI


urlpatterns = [
    url(
        r'^api/events/$',
        PublishAPI.as_view(), name='publish_api'
    ),
]
