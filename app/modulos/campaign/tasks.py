from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

