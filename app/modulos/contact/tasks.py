import requests
from celery import shared_task
from .models import Contact, Tag
from .utils import *
import os
from django.conf import settings
import requests
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync

@shared_task
def process_excel_file(file_name, file_path, name_column, number_column, limit, allow_duplicates, tags, user_id):
    try:
        webhookSend(user_id,'initial','lendo planilha ...', file_name)
        handler = ExcelHandler(file_path)
        contacts = handler.get_contacts(number_column, name_column, limit)
        
        total_contacts = len(contacts)
        created_contacts = []

        for index, contact in enumerate(contacts):
            name = contact.get('name')
            number = contact.get('number')
            if not allow_duplicates and Contact.objects.filter(user_id=user_id, number=number).exists():
                continue
            new_contact = Contact.objects.create(user_id=user_id, name=name, number=number)
            if new_contact:
                created_contacts.append(new_contact)
            if tags:
                tag_objects = Tag.objects.filter(id__in=tags, user_id=user_id)
                if tag_objects.exists():
                    new_contact.tags.set(tag_objects)

            # Calcular progresso e enviar mensagem
            if index % 10 == 0:
                progress_percent = int(((index + 1) / total_contacts) * 100)
            webhookSend(user_id, 'saving', 'salvando ...', file_name, progress_percent)

        #webhookSend('complete','Processamento completo!')
        if file_path and os.path.exists(file_path):
            os.remove(file_path)

        webhookSend(user_id,'complete','Completo', file_name, progress_percent)
        return f'[COMPLETE] >> CONTATOS SALVOS {len(created_contacts)}' 

    except Exception as e:
        webhookSend(user_id,'error', f'error ao criar contatos {str(e)}', file_name, progress_percent)
        return f'[ERROR TASKS] >> {str(e)}'

@shared_task
def webhookSend(user_id, status, message, file_name, porcent=None):
    try:
        if not user_id and status and message and porcent:
            return None
        #webhook_url = f'{settings.BASE_URL}/webhook/progress/'
        data = {
            'user_id': user_id,
            'status': status,
            'message': message,
            'porcent': porcent,
            'filename': file_name
        }
        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
                f'progress_{user_id}',
                    {
                    'type': 'progress',
                    'progress': data
                }
            )
        #requests.post(webhook_url, data=json.dumps(data), headers={'Content-Type': 'application/json'})
    except Exception as e:
        print('Error sending data to webhook:', str(e))
  
   