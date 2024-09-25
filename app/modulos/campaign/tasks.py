from celery import shared_task
from app.modulos.contact.models import Contact, Tag
from app.modulos.instance.models import Instance
from .models import SendMensagem , Campaign
import random
import time
import requests
from celery_progress.backend import ProgressRecorder
from celery import shared_task
from django.utils import timezone
import random
import time
import requests

@shared_task(bind=True)
def process_campaign_contacts(self, campaign_id, tag_name, contact_name):
        
        # Set up the progress recorder
        progress_recorder = ProgressRecorder(self)
        
        campaign = Campaign.objects.get(id=campaign_id)
        contacts = Contact.objects.filter(user=campaign.user)

        if tag_name:
            tag = Tag.objects.filter(user=campaign.user, name__icontains=tag_name).first()
            if tag:
                contacts = contacts.filter(tags=tag)

        if contact_name:
            contacts = contacts.filter(name__icontains=contact_name)

        
        instance = list(campaign.instance.all())

        if campaign.start_number < 1 or campaign.start_number > len(contacts):
            raise ValueError(f"O número de início ({campaign.start_number}) está fora do intervalo válido de contatos (1 a {len(contacts)}).")

        if campaign.end_number < campaign.start_number or campaign.end_number > len(contacts):
            raise ValueError(f"O número final ({campaign.end_number}) está fora do intervalo válido de contatos (1 a {len(contacts)}).")

        # Define o início e o fim baseado nos valores válidos
        inicio = campaign.start_number - 1  # Subtraindo 1 para transformar em índice de lista (0-based index)
        fim = campaign.end_number - 1
        
        campaign.total_numbers = campaign.end_number if campaign.end_number else len(contacts)
        campaign.save()

        # Outras variáveis e lógicas
        min_interval = campaign.start_timeout
        max_interval = campaign.end_timeout
        total_milliseconds = 0

        numeros_enviados = []
        intervalos = []
        
        if campaign.enable_pause:
            for _ in range(campaign.pause_quantity):
                intervalos.append(random.randint(inicio, fim))

        contacts_sent = 0  # Keep track of contacts processed

        
        # Verifica duplicados com mais segurança e ajusta a lógica de instâncias
        for i in range(inicio, fim + 1):
            time_interval = 0
            if i in intervalos:
                time_interval += random.randint(campaign.min_pause, campaign.max_pause) * 60

            contact = contacts[i]
            numero_celular = contact.number
            nome = contact.name if contact.name else "Colaborador"

            random_interval = random.randint(min_interval, max_interval)

            # Certifique-se de verificar se o número já foi enviado antes de tentar enviar novamente
            if numero_celular and numero_celular not in numeros_enviados:
                # Verifique se há mais de uma instância e selecione adequadamente
                inst = instance[contacts_sent % len(instance)] if instance else None

                # Enviar a mensagem
                status, code, msg = enviar_mensagem_whatsapp(inst, numero_celular, nome, i)
                SendMensagem.objects.create(
                    campaign=campaign,
                    numero=numero_celular,
                    status=status,
                    code=code,
                    msg=msg
                )

                # Atualize o status da campanha
                if status == 'sucesso':
                    campaign.send_success += 1
                else:
                    campaign.send_erro += 1

                numeros_enviados.append(numero_celular)
                campaign.save()

            # Atraso entre as mensagens
            time.sleep(random_interval + time_interval)

            contacts_sent += 1

            # Atualize o progresso
            progress_recorder.set_progress(contacts_sent, campaign.total_numbers, description=f"Enviando para {contact.name or 'Colaborador'}")

        total_minutes = total_milliseconds // 60000
        end_time = timezone.now() + timezone.timedelta(minutes=total_minutes)
        campaign.end_time = end_time
        campaign.save()

        print(f"Disparo iniciado. Tempo total: {total_minutes // 60} horas e {total_minutes % 60} minutos")

        return {'success': True, 'task_id': self.request.id, 'progress': 100}

def enviar_mensagem_whatsapp(instance, numero, nome, i):
    """Função auxiliar para enviar mensagem via API"""
    mensagens = [
        f"👋 Oi, {nome}! Como você está?",
        f"Como vai?, {nome}! Tudo certo?",
        f"E aí, {nome}! Tudo bem com você?",
        f"Tranquilo?, {nome}! Como vão as coisas?",
        f"👋 Oi, {nome}! Tudo jóia?",
        f"Olá, {nome}! Espero que esteja bem!",
        f"Opa, {nome}! Como está indo?",
        f"Tudo bem com você, {nome}?",
        f"Olá, {nome}! Que prazer te ver!",
        f"Como vai seu dia ?, {nome}! Tudo tranquilo?",
        f"Oi, {nome}! Como estão as coisas?",
        f"Tudo em ordem por aí?, {nome}",
        f"E aí, {nome}! Tudo certo?",
        f"{nome} Tudo legal?",
        f"Olá, {nome}! Espero que esteja ótimo!",
        f"Iae, {nome}! Como está se sentindo?",
        f"Olá, {nome}! Tudo em paz?",
        f"De boa?, {nome}! Que bom te ver!",
        f"Fala comigo, {nome}! Como vai?",
        f"{nome}? Tudo bem com você?"
    ]

    mensagem = random.choice(mensagens)
    url = f"https://api.star.dev.br/message/sendText/{instance.name}"
    headers = {
        'apikey': instance.token,
    }
    payload = {
        "number": '5521981345727',
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
        # Tenta enviar a mensagem
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()

        # Sucesso ao enviar a mensagem
        print(f"Mensagem enviada com sucesso para {numero} de {instance.name} - Mensagem {i}")
        return 'sucesso', response.status_code, f"[instancia] {instance.name} {response.text}"

    except requests.exceptions.RequestException as e:
        # Tenta capturar o código de status e a mensagem da resposta, se existir
        if e.response is not None:
            code = e.response.status_code
            message = f"[instancia] {instance.name} {e.response.text}"   # Captura a mensagem de erro da resposta
        else:
            code = 500  # Código genérico caso não exista resposta do servidor
            message = f"[instancia] {instance.name} Error ao enviar mensagem"  # Mensagem padrão da exceção

        # Retorna o erro com o código e a mensagem correta
        print(f"Erro ao enviar mensagem para {numero}: {message}")
        return 'erro', code, message
    
        