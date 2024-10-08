from celery import group
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.utils import timezone
from app.modulos.contact.models import Contact, Tag
from app.modulos.instance.models import Instance
from .models import SendMensagem, Campaign, CampaignMessage
import random
import time
import requests

CHUNK_SIZE = 250 

@shared_task(bind=True)
def enviar_mensagens_para_grupo(self, campaign_id, contacts_chunk):
    """
    Subtarefa que envia mensagens para um grupo de contatos. 
    Processa um bloco de contatos em paralelo.
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        instances = list(campaign.instance.all())  # Obtém as instâncias associadas à campanha
        if not instances:
            raise ValueError("Nenhuma instância associada à campanha.")

        contacts_sent = []
        progress_recorder = ProgressRecorder(self)

        for idx, contact in enumerate(contacts_chunk):
            numero_celular = contact.number
            nome = contact.name or "Colaborador"
            instance = instances[idx % len(instances)]  # Seleciona a instância de forma cíclica

            # Envia a mensagem e captura o status
            status, code, msg = enviar_mensagem_whatsapp(instance, numero_celular, nome, idx)

            # Registra o envio da mensagem imediatamente
            SendMensagem.objects.create(
                campaign=campaign,
                numero=numero_celular,
                status=status,
                code=code,
                msg=msg
            )

            # Se a mensagem foi enviada com sucesso, registra a resposta pendente
            if status == 'sucesso':
                CampaignMessage.objects.create(
                    campaigns=[campaign],  # Associando a campanha
                    instance=instance,
                    numero=numero_celular,
                    status='pendente'  # Iniciando como pendente
                )

            # Atualiza o progresso da tarefa
            progress_recorder.set_progress(idx + 1, len(contacts_chunk))
        
        
        # Atualiza o progresso da campanha
        campaign.send_success += sum(1 for msg in contacts_sent if msg.status == 'sucesso')
        campaign.send_error += sum(1 for msg in contacts_sent if msg.status == 'erro')
        campaign.save()

        return {'success': True, 'total_sent': len(contacts_sent)}
    except Exception as e:
        print(f"Erro ao processar grupo de contatos: {str(e)}")
        raise ValueError(f"Erro ao processar grupo de contatos: {str(e)}")


def enviar_mensagem_whatsapp(instance, numero, nome, message_number):
    """
    Função auxiliar para enviar mensagens via API do WhatsApp.
    """
    if not instance:
        return 'erro', 500, 'Instância é None.'

    mensagens = [
        f"👋 Oi, {nome}! Como você está?",
        f"Como vai, {nome}? Tudo certo?",
        f"E aí, {nome}! Tudo bem com você?",
        f"Tranquilo, {nome}? Como vão as coisas?",
        f"👋 Oi, {nome}! Tudo jóia?",
        f"Olá, {nome}! Espero que esteja bem!",
        f"Opa, {nome}! Como está indo?",
        f"Tudo bem com você, {nome}?",
        f"Olá, {nome}! Que prazer te ver!",
        f"Como vai seu dia, {nome}? Tudo tranquilo?",
    ]

    mensagem = random.choice(mensagens)
    url = f"https://api.star.dev.br/message/sendText/{instance.name}"
    headers = {
        'apikey': instance.token,
    }
    payload = {
        "number": numero,
        "options": {
            "delay": 2300,
            "presence": "composing",
            "linkPreview": False
        },
        "textMessage": {
            "text": mensagem
        }
    }

    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Mensagem enviada com sucesso
        print(f"Mensagem enviada com sucesso para {numero} de {instance.name} - Mensagem {message_number}")
        return 'sucesso', response.status_code, f"[instância] {instance.name} {response.text}"

    except requests.exceptions.RequestException as e:
        code = e.response.status_code if e.response else 500
        message = f"[instância] {instance.name} Erro ao enviar mensagem: {str(e)}"
        print(f"Erro ao enviar mensagem para {numero}: {message}")
        return 'erro', code, message