import random
import string
from django.utils import timezone
from django.db import models
from django.contrib.auth.models import User
from app.modulos.instance.models import Instance

class Campaign(models.Model):
    name = models.CharField(max_length=255)  # Nome da campanha
    total_numbers = models.IntegerField(null=True, blank=True)  # Quantidade total de números a serem enviados
    sent_numbers = models.IntegerField(default=0)  # Quantidade de números já enviados
    start_date = models.DateTimeField()  # Data de início da campanha
    end_date = models.DateTimeField(null=True, blank=True)  # Data de término da campanha
    tracking_code = models.CharField(max_length=12, unique=True, editable=False)  # Código de rastreio aleatório
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Usuário que criou a campanha
    start_timeout = models.IntegerField()  # Tempo de início do sorteio do timeout em segundos
    end_timeout = models.IntegerField()  # Tempo final do sorteio do timeout em segundos
    send_greeting = models.BooleanField(default=False)  # Mensagem de saudação (boolean)
    id_progress = models.CharField(max_length=200)  # ID do progresso da tarefa no celery-progress
    instance = models.ForeignKey(Instance, on_delete=models.CASCADE, related_name='campaigns')  # Instância

    # Campos de configuração de envio
    start_number = models.IntegerField()  # Número inicial para envio
    end_number = models.IntegerField()  # Número final para envio

    # Configurações de pausa entre mensagens
    enable_pause = models.BooleanField(default=False)  # Habilitar pausas entre mensagens
    min_pause = models.IntegerField(null=True, blank=True)  # Pausa mínima (minutos)
    max_pause = models.IntegerField(null=True, blank=True)  # Pausa máxima (minutos)
    pause_quantity = models.IntegerField(null=True, blank=True)  # Quantidade de pausas

    # Função para gerar código de rastreio aleatório
    def generate_tracking_code(self):
        return ''.join(random.choices(string.ascii_letters + string.digits, k=12))

   
    def save(self, *args, **kwargs):
        # Sobrescreve o método save para gerar o código de rastreio ao salvar
        if not self.tracking_code:
            self.tracking_code = self.generate_tracking_code()

        # Define a data de início automaticamente se não for fornecida
        if not self.start_date:
            self.start_date = timezone.now()

        # Valida que se as pausas estão habilitadas, os campos min_pause, max_pause e pause_quantity devem estar preenchidos
        if self.enable_pause:
            if not self.min_pause or not self.max_pause or not self.pause_quantity:
                raise ValueError("Se as pausas estiverem habilitadas, 'min_pause', 'max_pause' e 'pause_quantity' devem ser preenchidos.")
            if self.min_pause > self.max_pause:
                raise ValueError("O valor de 'min_pause' não pode ser maior que 'max_pause'.")

        super().save(*args, **kwargs)


    def __str__(self):
        return f"Campanha: {self.name} - Tracking: {self.tracking_code}"
