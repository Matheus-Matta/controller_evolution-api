from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def webhookSend(self, user_id, status, message, porcent=None):
    try:
        if not (user_id and status and message and porcent is not None):
            print('Missing data for webhookSend, skipping...')
            return None
        data = {
            'user_id': user_id,
            'status': status,
            'message': message,
            'porcent': porcent
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'progress_{user_id}',
            {
                'type': 'progress',
                'progress': data
            }
        )
    except Exception as e:
        print('Error sending data to webhook:', str(e))
        self.retry(exc=e)