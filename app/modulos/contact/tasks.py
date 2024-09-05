from celery import shared_task
from .models import Contact, Tag
from .utils import ExcelHandler
import os
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.db import transaction

@shared_task
def process_excel_file(file_path, name_column, number_column, limit, allow_duplicates, tags, user_id):
    try:
        # Enviar mensagem inicial de leitura
        webhookSend.apply_async((user_id, 'initial', 'lendo planilha...', 0), queue='webhook')
        
        handler = ExcelHandler(file_path)
        contacts = handler.get_contacts(number_column, name_column, limit)
        total_contacts = len(contacts)
        created_contacts = []
        
        # Preparar os objetos Tag apenas uma vez
        tag_objects = Tag.objects.filter(id__in=tags, user_id=user_id) if tags else []

        with transaction.atomic():
            # Criar contatos em lote
            for contact in contacts:
                name = contact.get('name')
                number = contact.get('number')
                if allow_duplicates or not Contact.objects.filter(user_id=user_id, number=number).exists():
                    created_contacts.append(Contact(user_id=user_id, name=name, number=number))

            # Inserir todos os contatos de uma vez
            Contact.objects.bulk_create(created_contacts)

            # Associar tags aos novos contatos
            if tag_objects.exists():
                for contact in created_contacts:
                    contact.tags.set(tag_objects)

        # Enviar progresso e conclusão em lotes
        for index, contact in enumerate(created_contacts):
            if index % 50 == 0 or index == total_contacts - 1:
                progress_percent = int(((index + 1) / total_contacts) * 100)
                webhookSend.apply_async((user_id, 'saving', 'salvando...', progress_percent), queue='webhook')

        # Remover o arquivo de planilha se ele ainda existir
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        return f'[COMPLETE] >> CONTATOS SALVOS {len(created_contacts)}' 

    except Exception as e:
        webhookSend.apply_async((user_id, 'error', f'error ao criar contatos {str(e)}', 0), queue='webhook')
        return f'[ERROR TASKS] >> {str(e)}'

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
