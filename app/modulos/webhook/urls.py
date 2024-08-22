
from django.urls import path, include
from . import views

urlpatterns = [
    path('webhook',views.webhook_view, name='webhook'),
]