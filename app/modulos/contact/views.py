from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Contact
from .utils import *
from app.modulos.tags.models import Tag
import time
import os
from django.conf import settings
from django.http import JsonResponse
import json
from .tasks import *
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@login_required
def contact(request):
    data = {
            'user_id': 1,
            'status':2,
            'message': 3,
            'porcent': 4,
            'filename': 5
        }
    channel_layer = get_channel_layer()
    async_to_sync(channel_layer.group_send)(
                f'progress_1',
                    {
                    'type': 'progress',
                    'progress': data
                }
            )
    if request.method == 'GET':
        # Obtém todos os contatos do usuário
        # Enviar mensagem de progresso ao iniciar a leitura do arquivo
        query = request.GET.get('query')
        if query:
            contacts = Contact.objects.filter(name__icontains=query,user=request.user)
        else:
            contacts = Contact.objects.filter(user=request.user)
        # Configuração da paginação
        paginator = Paginator(contacts, 100)  # Mostra 100 contatos por página
        page_number = request.GET.get('page')  # Obtém o número da página da URL
        page_obj = paginator.get_page(page_number)  # Obtém os contatos da página atual
        # Total de contatos
        total_contacts = contacts.count()
        # Obtém as tags do usuário
        tags = Tag.objects.filter(user=request.user).distinct()
        # Renderiza o template com os contatos paginados
        return render(request, 'contacts.html', {
            'contacts': page_obj.object_list,  # Contatos da página atual
            'page_obj': page_obj,              # Objeto da página para controle no template
            'tags': tags,                      # Tags do usuário
            'total_contacts': total_contacts,  # Quantidade total de contatos
        })

    return redirect('user_login')

@login_required
def contact_create(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get('name')
            number = data.get('number')
            if not name or not number:
                return JsonResponse({'error': 'Nome e número são obrigatórios'}, status=400)
            if Contact.objects.filter(user=request.user, number=number).exists():
                return JsonResponse({'error': 'Esse numero para contato ja existe'}, status=400)
            contact = Contact.objects.create(user=request.user, name=name, number=number)
            contact_len = len(Contact.objects.filter(user=request.user))
            print(f'CREATE_CONTACT: [{request.user}] -> Name:{name} Number:{number}')
            contact_html = render_to_string('contact_load/partials/contact_item.html',{
                                            'contact': contact,
                                            'contact_len': contact_len
                                            })
            return JsonResponse({'message': 'Contato criado com sucesso!',
                                 'contact_html': contact_html,
                                 'contact_id': contact.id,
                                 'contact_len': contact_len },
                                status=201)
        except Exception as e:
            print(f"Erro ao criar contato: {e}")
            return JsonResponse({'error': 'Erro ao criar contato', 'details': str(e)}, status=500)

@login_required
def update_contact(request):
    if request.method == 'PUT':
        try:
            data = json.loads(request.body)
            id = data.get("id")
            name = data.get("name")
            number = data.get('number')
            contact = Contact.objects.get(id=id)
            msg = f"UPDATE: [{request.user}]  { contact.name} { contact.number} > {name} {number}"
            contact.name = name
            contact.number = number
            contact.save()
            print(msg)
        except contact.DoesNotExist:
            JsonResponse({'status': 'Error: contato não existe'}, status=400)
        except:
            print("ERROR AO ATUALIZAR O CONTATO")
            JsonResponse({'status': 'Error'}, status=400)

    return JsonResponse({'status': 'success'}, status=200)

def filter_contact_by_name(request):
    if request.method == 'GET':
        try:
            query = request.GET.get('query')
            if query:
                contacts = Contact.objects.filter(name__icontains=query,user=request.user)
            else:
                contacts = Contact.objects.filter(user=request.user)

            paginator = Paginator(contacts, 100)  # Mostra 100 contatos por página
            page_number = request.GET.get('page')  # Obtém o número da página da URL
            page_obj = paginator.get_page(page_number)  # Obtém os contatos da página atual
            total_contacts = contacts.count()
            # Obtém as tags do usuário
            tags = Tag.objects.filter(user=request.user).distinct()

            context =  {
                'contacts': page_obj.object_list,  # Contatos da página atual
                'page_obj': page_obj,              # Objeto da página para controle no template
                'tags': tags,                      # Tags do usuário
                'total_contacts': total_contacts,  # Quantidade total de contatos
            }
            # Renderiza o template com os contatos paginados
            html = render_to_string('list_contacts.html', context)
            return JsonResponse({'status': 'success', 'list_contact': html}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
    return redirect('user_login')
    

@login_required
def delete_contacts(request):
    if request.method == 'DELETE':
        try:
            data = json.loads(request.body)
            contacts_ids = data.get("contacts")
            if not contacts_ids:
                return JsonResponse({'status': 'error', 'message': 'Contatos não fornecidos'}, status=400)
            contacts = Contact.objects.filter(id__in=contacts_ids, user=request.user)
            contacts.delete()[0]
            messages.success(request,  f'{len(contacts_ids)} contatos excluídos com sucesso!')
            print(f"[{request.user}] Contatos Excluidos: -> {len(contacts_ids)}")
            return JsonResponse({'status': 'success'}, status=200)
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': 'Houve um problema ao excluir os contatos', 'details': str(e)}, status=500)

    return redirect('user_login')



def import_contact(request):
    if request.method == 'POST':
        try:
            # Recebe os parâmetros do request
           
            name_column = request.POST.get('name_column')
            number_column = request.POST.get('number_column')
            limit = int(request.POST.get('limit_rows')) if request.POST.get('limit_rows') else None
            allow_duplicates = request.POST.get('allow_duplicates')
            tags = request.POST.getlist('tags')
            if not request.FILES:
                return JsonResponse({'status': 'error', 'message': 'Arquivo está vazio!'})
            if not name_column:
                return JsonResponse({'status': 'error', 'message': 'Coluna de nome não informada!'})
            if not number_column:
                return JsonResponse({'status': 'error', 'message': 'Coluna de numero não informada!'})

            
            # Recebe o arquivo enviado
            uploaded_file = request.FILES['excel_file']
            file_extension = uploaded_file.name.split('.')[-1].lower()

            if file_extension not in ['xls', 'xlsx']:
                return JsonResponse({'status': 'error', 'message': 'O arquivo enviado não é um arquivo Excel válido.'})

            timestamp = int(time.time() * 1000)
            file_name = f"{request.user}_{timestamp}.{file_extension}"
            file_path = os.path.join(settings.MEDIA_ROOT, 'uploaded_files', file_name)

            os.makedirs(os.path.dirname(file_path), exist_ok=True)

            with open(file_path, 'wb') as f:
                for chunk in uploaded_file.chunks():
                    f.write(chunk)
           
           # Chama a tarefa Celery para processar o arquivo Excel em segundo plano
            process_excel_file.delay(file_name, file_path, name_column, number_column, limit, allow_duplicates, tags, request.user.id)
            return JsonResponse({'status': 'success','message':'O processo de importação foi iniciado. Você será notificado quando estiver concluído.'},status=201)
        except Exception as e:
            print(e)
            return JsonResponse({'status': 'error', 'message':'error ao salvar contato: '+str(e)})
    return redirect('contact')

