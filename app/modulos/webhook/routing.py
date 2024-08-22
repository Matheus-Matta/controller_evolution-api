
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/webhook/(?P<user_id>\d+)/$', consumers.WebhookConsumer.as_asgi()),
]