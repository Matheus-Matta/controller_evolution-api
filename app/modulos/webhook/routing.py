
from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/webhook/(?P<user_id>\d+)/$', consumers.WebhookConsumer.as_asgi()),
    re_path(r'ws/webhook/progress/(?P<user_id>\d+)/$', consumers.ProgressConsumer.as_asgi()),
]