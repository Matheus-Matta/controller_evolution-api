
from django.urls import path, include
from . import views

urlpatterns = [
    path('campanha', views.campanha, name='campanha'),
]