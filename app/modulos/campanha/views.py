from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

from app.modulos.instance.models import Instance
from app.modulos.instance.forms import InstanceForm

@login_required
def campanha(request):
    return render()