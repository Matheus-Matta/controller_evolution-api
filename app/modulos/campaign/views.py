from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from app.modulos.instance.models import Instance
from app.modulos.instance.forms import InstanceForm
from .forms import CampaignForm 
from app.modulos.tags.models import Tag
from app.modulos.contact.models import Contact
from app.modulos.instance.models import Instance

from app.modulos.contact.utils import get_contacts
from django.contrib import messages
from .models import Campaign
from django.utils import timezone

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
               print(e)
               messages.error(request,  f'error ao tentar entra na campanha {str(e)}')
               return redirect("user_login")
          
     elif request.method == 'POST':
          try:
               name = request.POST.get('name')
               start_number = request.POST.get('start_number')
               end_number = request.POST.get('end_number')
               enable_pause = request.POST.get('enable_pause', False)
               min_pause = request.POST.get('min_pause')
               max_pause = request.POST.get('max_pause')
               pause_quantity = request.POST.get('pause_quantity')
               send_greeting = request.POST.get('send_greeting')
               start_timeout = request.POST.get('start_timeout')
               end_timeout = request.POST.get('end_timeout')
               instance = Instance.objects.get(user=request.user, id=request.POST.get('instance'))

               tag_name = request.POST.get('tag_name')
               contact_name = request.POST.get('contact_name')

               # Salvar campanha no banco de dados
               campaign = Campaign.objects.create(
                    name=name,
                    start_number=start_number,
                    end_number=end_number,
                    start_date=timezone.now(),
                    start_timeout=start_timeout,
                    end_timeout=end_timeout,
                    send_greeting=bool(send_greeting),
                    enable_pause=bool(enable_pause),
                    min_pause=min_pause if enable_pause else None,
                    max_pause=max_pause if enable_pause else None,
                    pause_quantity=pause_quantity if enable_pause else None,
                    user=request.user,
                    instance=instance
               )

               # Chama a task para processar os contatos (descomentar quando a task estiver definida)
               # process_campaign_contacts.delay(campaign.id, tag_name, contact_name)
               print(campaign)
               messages.success(request, 'Campanha criada com sucesso!')
               return redirect("user_login")
          except Exception as e:
               print(f'[campaign] error {str(e)}')
               messages.error(request,  f'error ao iniciar a campanha {str(e)}')
               return redirect("user_login") 
