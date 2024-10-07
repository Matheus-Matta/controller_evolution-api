
from celery import shared_task
from celery_progress.backend import ProgressRecorder
from django.utils import timezone

from app.modulos.contact.models import Contact, Tag
from app.modulos.instance.models import Instance
from .models import SendMensagem, Campaign

import random
import time
import requests

@shared_task(bind=True)
def process_campaign_contacts(self, campaign_id, tag_name=None, contact_name=None):
    try:
        """
        Tarefa Celery para processar contatos de campanha e enviar mensagens.
        """
        progress_recorder = ProgressRecorder(self)

        # Recupera a campanha ou lança um erro se não existir
        try:
            campaign = Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            raise ValueError(f"Campanha com id {campaign_id} não existe.")

        # Filtra os contatos com base no usuário da campanha
        contacts = Contact.objects.filter(user=campaign.user)

        # Aplica filtros opcionais de tag e nome de contato
        if tag_name:
            tag = Tag.objects.filter(user=campaign.user, name__icontains=tag_name).first()
            if tag:
                contacts = contacts.filter(tags=tag)

        if contact_name:
            contacts = contacts.filter(name__icontains=contact_name)

        # Ordena os contatos para garantir uma ordem consistente
        contacts = contacts.order_by('id')

        total_contacts = contacts.count()
        if total_contacts == 0:
            raise ValueError("Nenhum contato encontrado para a campanha.")

        # Define números de início e fim padrão se não estiverem definidos
        start_number = campaign.start_number or 1
        end_number = campaign.end_number or total_contacts

        # Valida os números de início e fim
        if start_number < 1 or start_number > total_contacts:
            raise ValueError(f"O número de início ({start_number}) está fora do intervalo válido (1 a {total_contacts}).")

        if end_number < start_number or end_number > total_contacts:
            raise ValueError(f"O número final ({end_number}) está fora do intervalo válido ({start_number} a {total_contacts}).")

        # Ajusta índices para indexação baseada em zero
        inicio = start_number - 1
        fim = end_number - 1

        # Atualiza o total de números na campanha
        campaign.total_numbers = end_number - start_number + 1
        campaign.save()

        # Define intervalos mínimos e máximos com valores padrão se necessário
        min_interval = campaign.start_timeout or 0
        max_interval = campaign.end_timeout or 0

        if min_interval > max_interval:
            raise ValueError("O tempo de início não pode ser maior que o tempo de término.")

        # Gera índices de pausa únicos se as pausas estiverem habilitadas
        intervalos = []
        if campaign.enable_pause and campaign.pause_quantity:
            total_messages = fim - inicio + 1
            pause_quantity = min(campaign.pause_quantity, total_messages)
            intervalos = random.sample(range(inicio, fim + 1), pause_quantity)

        # Obtém a lista de contatos relevantes
        contacts_list = contacts[inicio:fim + 1]

        # Recupera as instâncias associadas à campanha
        instances = list(campaign.instance.all())
        if not instances:
            raise ValueError("Nenhuma instância associada à campanha.")

        contacts_sent = 0  # Contador de contatos processados
        start_time = time.time()  # Marca o tempo de início

        for idx, contact in enumerate(contacts_list, start=inicio):
            time_interval = 0
            if idx in intervalos:
                # Adiciona tempo de pausa em segundos
                time_interval += random.randint(campaign.min_pause, campaign.max_pause) * 60

            numero_celular = contact.number
            nome = contact.name if contact.name else "Colaborador"

            # Gera um intervalo aleatório entre as mensagens
            random_interval = random.randint(min_interval, max_interval)

            if numero_celular:
                try:
                    # Seleciona a instância de forma cíclica
                    inst = instances[contacts_sent % len(instances)]

                    # Envia a mensagem e captura o status
                    status, code, msg = enviar_mensagem_whatsapp(inst, numero_celular, nome, idx)
                    SendMensagem.objects.create(
                        campaign=campaign,
                        numero=numero_celular,
                        status=status,
                        code=code,
                        msg=msg
                    )

                    # Atualiza contadores da campanha
                    if status == 'sucesso':
                        campaign.send_success += 1
                    else:
                        campaign.send_error += 1

                    campaign.save()
                    contacts_sent += 1

                    # Atualiza o progresso da tarefa
                    progress_recorder.set_progress(contacts_sent, campaign.total_numbers, description=f"Enviando para {nome}")

                except Exception as e:
                    # Loga o erro e continua a execução
                    print(f"Erro ao enviar mensagem para {numero_celular}: {str(e)}")
                    # Salva o erro no SendMensagem
                    SendMensagem.objects.create(
                        campaign=campaign,
                        numero=numero_celular,
                        status='erro',
                        code=500,
                        msg=str(e)
                    )
                    
                    # Atualiza contadores de erro
                    campaign.send_error += 1
                    campaign.save()
                    contacts_sent += 1

                    # Atualiza o progresso da tarefa
                    progress_recorder.set_progress(contacts_sent, campaign.total_numbers, description=f"Erro ao enviar para {nome}")

            # Aguarda o intervalo calculado antes de enviar a próxima mensagem
            total_sleep = random_interval + time_interval
            time.sleep(total_sleep)

        end_time = time.time()
        total_seconds = end_time - start_time
        total_minutes = int(total_seconds // 60)
        hours, minutes = divmod(total_minutes, 60)

        # Atualiza o status da campanha para 'finalizado'
        campaign.end_date = timezone.now()
        campaign.status = 'finalizado'
        campaign.save()

        print(f"Disparo finalizado. Tempo total: {hours} horas e {minutes} minutos")

        return {'success': True, 'task_id': self.request.id, 'progress': 100}
    except Exception as e:
        print(f"Erro exception {e}")
        raise ValueError("Erro ao iniciar campanha.")

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
        f"Oi, {nome}! Como estão as coisas?",
        f"Tudo em ordem por aí, {nome}?",
        f"E aí, {nome}! Tudo certo?",
        f"{nome}, tudo legal?",
        f"Olá, {nome}! Espero que esteja ótimo!",
        f"E aí, {nome}! Como está se sentindo?",
        f"Olá, {nome}! Tudo em paz?",
        f"De boa, {nome}? Que bom te ver!",
        f"Fala comigo, {nome}! Como vai?",
        f"{nome}, tudo bem com você?"
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
