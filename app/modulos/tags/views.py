from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib import messages
from app.modulos.contact.models import Contact
from .models import Tag
from django.http import JsonResponse
import json
from django.core.paginator import Paginator
from .tasks import add_tags_to_contacts_task

@login_required
def create_tag(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            name = data.get("name")
            if not name:
                return JsonResponse({'message': 'Nome da tag não fornecido'}, status=400)
            tag_exists = Tag.objects.filter(user=request.user, name=name).exists()
            if tag_exists:
                return JsonResponse({'message': 'Tag já existe!', 'tag': {'name': name}}, status=200)
            tag = Tag.objects.create(user=request.user, name=name)
            modal_tag_html = render_to_string('contact_load/partials/modal_tag_item.html',{'tag': tag})
            tag_html = render_to_string('contact_load/partials/tag_item.html',{'tag': tag})

            return JsonResponse({'message': 'Tag criada com sucesso!', 'tag': {'id': tag.id, 'tag_html': tag_html, 'modal_tag_html': modal_tag_html}}, status=201)
        except Exception as e:
            print(e)
            return JsonResponse({'message': 'Houve um problema interno ao criar a tag', 'details': str(e)}, status=500)
    return redirect('user_login')

@login_required
def add_tags_to_contacts(request):
    if request.method == 'POST':
       if request.method == 'POST':
        try:
            data = json.loads(request.body)
            contact = data.get("contacts")
            tags_id = data.get("tags")

            if not contact or not tags_id:
                return JsonResponse({'error': 'Contatos ou tags não fornecidos'}, status=400)

            # Chame a tarefa Celery
            add_tags_to_contacts_task.apply_async(args=(request.user.id, contact, tags_id), queue='default')

            # Retorne uma resposta imediata ao cliente
            return JsonResponse({'message': 'Processamento em segundo plano iniciado. Você será notificado ao término.'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Houve um problema ao adicionar as tags aos contatos', 'details': str(e)}, status=500)
    return redirect('user_login')

@login_required
def delete_tag(request):
    if request.method == 'POST':
        try:
            tag_id = request.POST.get("tag_id")
            if not tag_id:
                 messages.error(request,'ID da tag não fornecido!')
            tag = Tag.objects.filter(id=tag_id, user=request.user).first()
            if not tag:
                messages.error(request, 'Tag não encontrada!')
            else:
                tag.delete() # deleta tag
                messages.success(request, 'Tag deletada com sucesso!')
        except Exception as e:
           messages.error(request, f'Erro interno: {str(e)}')
    return redirect("contact")   
