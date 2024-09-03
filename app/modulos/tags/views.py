from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.contrib import messages
from app.modulos.contact.models import Contact
from .models import Tag
from django.http import JsonResponse
import json
from django.core.paginator import Paginator

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
        try:
            data = json.loads(request.body)
            contact = data.get("contacts")
            tags_id = data.get("tags")
            if not contact or not tags_id:
                    return JsonResponse({'error': 'Contatos ou tags não fornecidos'}, status=400)
            if contact == "all":
                contacts = Contact.objects.filter(user=request.user)
            else:    
                contacts = Contact.objects.filter(id__in=contact, user=request.user)
            tags = Tag.objects.filter(id__in=tags_id, user=request.user)
            for contact in contacts:
                for tag in tags:
                    if tag not in contact.tags.all():
                        contact.tags.add(tag)
                        print(f"[{request.user}] Tag adicionada: {contact} -> {tag}")
            messages.success(request, f'Tags adicionadas a {len(contacts)} contatos com sucesso!')
            return JsonResponse({'message': 'Tags adicionadas aos contatos com sucesso!'}, status=200)
        except Exception as e:
            print(e)
            return JsonResponse({'error': 'Houve um problema ao adicionar as tags aos contatos', 'details': str(e)}, status=500)
    return redirect('user_login')

@login_required
def filter_contacts_by_tag(request, tag_name):
    if request.method == 'GET':
        try:
            tag = Tag.objects.filter(name=tag_name, user=request.user).first()
            if not tag:
                return redirect('contact')
            contacts = Contact.objects.filter(tags=tag, user=request.user)
            paginator = Paginator(contacts, 100)  # Mostra 100 contatos por página
            page_number = request.GET.get('page')  # Obtém o número da página da URL
            page_obj = paginator.get_page(page_number)  # Obtém os contatos da página atual
            # Total de contatos
            total_contacts = contacts.count()
            tags = Tag.objects.filter(user=request.user).distinct()
            return render(request, 'contacts.html', {
                'contacts': page_obj.object_list,  # Contatos da página atual
                'page_obj': page_obj, # Objeto da página para controle no template
                'tags': tags, 
                'tag_name': tag.name, # Tags do usuário
                'total_contacts': total_contacts,
                'filter': True  # Quantidade total de contatos
            })
        except Exception as e:
            print(e)
            messages.error(request, 'Essa tag não existe!')
            return redirect('contact')
    return redirect('user_login')

@login_required
def delete_tag(request):
    print(request.POST, request.body)
    if request.method == 'POST':
        try:
            tag_id = request.POST.get("tag_id")
            if not tag_id:
                 messages.error(request,'ID da tag não fornecido!')
            tag = Tag.objects.filter(id=tag_id, user=request.user).first()
            if not tag:
                messages.error(request, 'Tag não encontrada!')
            else:
                tag.delete()
                messages.success(request, 'Tag deletada com sucesso!')
        except Exception as e:
           messages.error(request, f'Erro interno: {str(e)}')
    return redirect("contact")   
