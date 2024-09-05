# tasks.py
from celery import shared_task
from django.db import transaction
from .models import Tag
from app.modulos.contact.models import Contact
from app.modulos.webhook.tasks import webhookSend

@shared_task
def add_tags_to_contacts_task(user_id, contact_ids, tag_ids):
    try:
        webhookSend.apply_async((user_id, 'initial', 'iniciando...', 0), queue='webhook')

        with transaction.atomic():
            contacts = Contact.objects.filter(id__in=contact_ids, user_id=user_id)
            tags = Tag.objects.filter(id__in=tag_ids, user_id=user_id)
            total_contacts = len(contacts)
            progress_percent = 0  # Inicialize o progresso

            for index, contact in enumerate(contacts):
                for tag in tags:
                    if tag not in contact.tags.all():
                        contact.tags.add(tag)

                # Atualiza o progresso a cada 2 contatos ou no final
                if index % 2 == 0 or index == total_contacts - 1:
                    progress_percent = int(((index + 1) / total_contacts) * 100)
                    webhookSend.apply_async((user_id, 'saving', 'adicionando...', progress_percent), queue='webhook')

        webhookSend.apply_async((user_id, 'complete', 'finalizando', 100), queue='webhook')
        return {'status': 'success', 'message': f'Tags adicionadas a {total_contacts} contatos com sucesso!'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}