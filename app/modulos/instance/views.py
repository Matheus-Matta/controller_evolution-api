from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .sets import *
from .forms import *
from .request import *


@login_required
def create_instancia(request):
    if request.method == 'POST':
        try:
            form = InstanceForm(request.POST)
            if form.is_valid():
                    instance = form.save(commit=False)
                    public_name = instance.name
                    instance.name = f'{request.user}{instance.name}'
                    response = instance_create(instance)
                    if response.status_code == 201:
                        
                        instance_data = response.json()
                        instance.integration_type = f"WHATSAPP-{instance.integration_type.upper()}"
                        instance.instance_id = instance_data['instance']['instanceId']
                        instance.token = instance_data['hash']['apikey']
                        instance.user = request.user
                        instance.public_name = public_name 
                        print(instance)
                        instance.save()
    
                        qrcode_image = instance_data['qrcode']['base64']

                        web_response = setWebwook(instance.name, instance.token)
                        if web_response.status_code != 200:
                            messages.error(request, 'Houve um error ao conectar webhook a instacia')
                        instances = Instance.objects.filter(user=request.user)
                        messages.success(request, 'Instancia Criada com sucesso!')
                        return render(request, 'home.html', {
                            'user': request.user,
                            'qrcode_image': qrcode_image,
                            'instance':{
                                'name': instance.name,
                                'token': instance.token
                            },
                            'instances': instances
                        })
                    else:
                        messages.error(request, 'Houve um erro ao criar a instancia')
                        print(response.json())
            else:
                print("formulario invalido")
                form = InstanceForm()
                return render(request, 'home.html', {'user': request.user, 'form_instancia': form})
        except Exception as e:
            print(e)
            messages.error(request, 'Houve um problema interno')
            return redirect('user_login')

    return redirect('user_login')

def instance_detail(request, id):
    if request.method == 'GET':
        try:
            instance = Instance.objects.get(user=request.user,id=id)
            if instance:
                return render(request, 'instance_detail.html', {'user': request.user, 'instance': instance})
            else:
                messages.error("Essa instancia não existe")
                return redirect("user_login")
        except Exception as e:
            print(e)
            return redirect("user_login")
    
def delete_instance(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        instance =  Instance.objects.get(user=request.user, id=id)
        response = instance_logout(instance)
        print(response)
        if response.status_code != 200:
            instance.delete()
        response = instance_delete(instance)
        if response.status_code == 200:
            messages.success(request, 'Sua instancia foi excluida')
            instance.delete()
        else:
            messages.error(request, 'Error ao tentar excluir a instancia')
    return redirect('user_login')

def connect_instance(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        instance =  Instance.objects.get(user=request.user, id=id)
        try:
            instance_logout(instance)
            response = instance_connect(instance)
            if response.status_code == 200:
                instance_data = response.json()
                qrcode_image = instance_data['base64']
                return render(request, 'instance_detail.html',{
                                    'user': request.user,
                                    'instance': instance,
                                    'qrcode_image': qrcode_image
                                    })
            else:
                messages.error(request, 'Error ao gerar qrcode de conexão')

        except:
            messages.error("Houve um problema interno!")
    return redirect('user_login')

def restart_instance(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        instance =  Instance.objects.get(id=id)
        response = instance_restart(instance)
        print(response.json())
        if response.status_code == 200:
            messages.success(request, 'Sua Instancia foi reiniciada')
        else:
            messages.error(request, 'Houve um problema ao tenta reiniciar a instancia')
    return redirect('instance_detail', id)

def logout_instance(request):
    if request.method == 'POST':
        id = request.POST.get('id')
        instance =  Instance.objects.get(id=id)
        response = instance_logout(instance)
        if response.status_code == 200:
            messages.success(request, 'Sua Instancia foi desconectada')
        else:
            messages.error(request, 'Houve um problema ao tenta desconectar a instancia')
    return redirect('instance_detail', id)