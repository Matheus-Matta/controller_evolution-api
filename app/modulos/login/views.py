from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from asgiref.sync import async_to_sync
from app.modulos.instance.models import Instance
from app.modulos.instance.forms import InstanceForm
from .forms import LoginForm

def user_login(request):
    if request.user.is_authenticated: # para verificar se está autenicado
        instancia = request.GET.get('new_instancia')
        if instancia:
            instancia = InstanceForm()
        instances = Instance.objects.filter(user=request.user)
        return render(request, 'home.html', {'user': request.user, 'form_instancia': instancia, 'instances': instances }) # Redireciona por que o usuario está autenticado
    
    if request.method == 'POST': # form de login 
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                instances = Instance.objects.filter(user=request.user) 
                return render(request, 'home.html', {'user': user, 'instances': instances })  # Redireciona após o login
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form}) # user não está logado

@login_required
def user_logout(request):
    logout(request)
    return redirect('user_login')
