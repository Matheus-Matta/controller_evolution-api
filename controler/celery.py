# celery.py

from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# Define o módulo de configurações padrão para o Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controler.settings')
os.environ.setdefault('FORKED_BY_MULTIPROCESSING', '1')

app = Celery('controler')

# Lê as configurações do Django no Celery
app.config_from_object('django.conf:settings', namespace='CELERY')

# Descobre e carrega automaticamente tarefas de todos os aplicativos Django
app.autodiscover_tasks()

# Definindo filas e rotas
app.conf.task_queues = {
    'default': {
        'exchange': 'default',
        'routing_key': 'default',
    },
    'webhook': {
        'exchange': 'webhook',
        'routing_key': 'webhook',
    },
    'messages': {
        'exchange': 'messages',
        'routing_key': 'messages',
    }
}

app.conf.task_routes = {
    'app.modulos.contact.tasks.webhookSend': {'queue': 'webhook'},
    'app.modulos.campaign.tasks.send_msg_task': {'queue': 'messages'},
}