import json
from channels.generic.websocket import AsyncWebsocketConsumer

class WebhookConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f'webhook_{self.user_id}'

        # Join the group for the specific user
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        # Leave the group for the specific user
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        message = json.loads(text_data)

        # Send message to the group
        await self.channel_layer.group_send(
            self.group_name,
            {
                'type': 'webhook_message',
                'message': message
            }
        )

    async def webhook_message(self, event):
        message = event['message']

        # Send message to WebSocket
        await self.send(text_data=json.dumps(message))

class ProgressConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user_id = self.scope['url_route']['kwargs']['user_id']
        self.group_name = f"progress_{self.user_id}"

        # Entra no grupo
        await self.channel_layer.group_add(
            self.group_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name,
            self.channel_name
        )

    # Processar mensagem recebida (se necessário)
    async def receive(self, text_data):
        print(text_data)

    # Atualização de progresso
    async def progress(self, event):
        if 'progress' in event:
            progress_data = event['progress']
            # Enviar mensagem de progresso para o WebSocket
            await self.send(text_data=json.dumps(progress_data))
        else:
            print('Progress key not found in event:', event)
   