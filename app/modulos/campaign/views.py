from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from asgiref.sync import async_to_sync
from app.modulos.instance.models import Instance
from app.modulos.instance.forms import InstanceForm
from .forms import CampaignForm 
from app.modulos.tags.models import Tag
from app.modulos.contact.models import Contact
from app.modulos.instance.models import Instance
from .tasks import process_campaign_contacts
from app.modulos.contact.utils import get_contacts
from django.contrib import messages
from .models import Campaign
from django.utils import timezone
from celery.result import AsyncResult
import time 
from django.urls import reverse


@login_required
def campaign(request):
    if request.method == 'GET':
        try:
            context = get_contacts(request)

            form = CampaignForm(user=request.user)
            context['form'] = form
            context['campaign'] = True

            return render(request, 'campaign.html', context)
        except Exception as e:
            print(f"[campaign GET] Error: {e}")
            messages.error(request, f"Erro ao tentar entrar na campanha: {str(e)}")
            return redirect("user_login")

    elif request.method == 'POST':
        try:
            # Coleta os dados do formulário
            name = request.POST.get('name')
            start_number = int(request.POST.get('start_number'))
            end_number = int(request.POST.get('end_number'))
            start_timeout = int(request.POST.get('start_timeout'))
            end_timeout = int(request.POST.get('end_timeout'))
            send_greeting = request.POST.get('send_greeting') == 'on'
            enable_pause = request.POST.get('enable_pause') == 'on'

            # Verifica se a pausa está habilitada e captura os valores
            min_pause = int(request.POST.get('min_pause')) if enable_pause else None
            max_pause = int(request.POST.get('max_pause')) if enable_pause else None
            pause_quantity = int(request.POST.get('pause_quantity')) if enable_pause else None

            # Coleta as instâncias selecionadas
            instances = Instance.objects.filter(user=request.user, id__in=request.POST.getlist('instance'))

            tag_name = request.POST.get('tag_name')
            contact_name = request.POST.get('contact_name')

            # Verifica se as instâncias foram selecionadas
            if not instances.exists():
                messages.error(request, "Nenhuma instância selecionada para a campanha.")
                return redirect("campaign")

            # Cria a campanha sem as instâncias (inicialmente)
            campaign = Campaign.objects.create(
                name=name,
                status='processando',
                start_number=start_number,
                end_number=end_number,
                start_date=timezone.now(),
                start_timeout=start_timeout,
                end_timeout=end_timeout,
                send_greeting=send_greeting,
                enable_pause=enable_pause,
                min_pause=min_pause,
                max_pause=max_pause,
                pause_quantity=pause_quantity,
                user=request.user
            )

            # Adiciona as instâncias
            campaign.instance.set(instances)

            # Chama a task de forma assíncrona, passando os parâmetros
            result = process_campaign_contacts.apply_async((campaign.id, tag_name, contact_name), queue='messages')

            # Associa o ID da task à campanha para poder monitorar o progresso
            campaign.id_progress = result.task_id
            campaign.save()

            # Redireciona para a página de progresso da campanha
            return redirect(reverse('campaign_progress', args=[result.task_id]))

        except Exception as e:
            print(f"[campaign POST] Error: {e}")
            messages.error(request, f"Erro ao iniciar a campanha: {str(e)}")
            return redirect("user_login")

@login_required
def campaign_progress(request, task_id):
    try:
        result = AsyncResult(task_id)
        campaign = Campaign.objects.get(id_progress=task_id)
    except Campaign.DoesNotExist:
        messages.error(request, "Campanha não encontrada.")
        return redirect('campaign')

    if result.ready():
        if result.state == 'FAILURE':
            error_message = str(result.result)
            messages.error(request, f"Erro na execução da campanha: {error_message}")
            return redirect("user_login")
        else:
            task_result = result.result
            if task_result.get('success', False):
                return render(request, 'progress.html', {'task_id': task_id, 'campaign': campaign})
            else:
                messages.error(request, task_result.get('message'))
                return redirect('campaign')
    else:
        return render(request, 'progress.html', {'task_id': task_id, 'status': 'in_progress', 'campaign': campaign})

# View para encerrar a campanha
@login_required
def encerrar_campaign(request, campaign_id):
     if request.method == "POST":
          try:
               campaign = Campaign.objects.get(id=campaign_id)
               if campaign.status != 'finalizado':
                    campaign.end_date = timezone.now()
                    campaign.status = 'cancelado'
                    campaign.save()
                    task_id = campaign.id_progress
                              
                    # Cancela a task no Celery
                    result = AsyncResult(task_id)
                    result.revoke(terminate=True)
                    messages.success(request, "Campanha encerrada com sucesso.")
               else:
                    messages.error(request, "Campanha ja encerrada.")
          except Campaign.DoesNotExist:
               messages.error(request, "Campanha não encontrada.")
          except Exception as e:
            messages.error(request, f"Erro ao encerrar a campanha: {str(e)}")
    
     return redirect('user_login')