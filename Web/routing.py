from django.conf.urls import url

from Web import consumers

websocket_urlpatterns = [
    url(r'^ws/$', consumers.updateResult),
]
