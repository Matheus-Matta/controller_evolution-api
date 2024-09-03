
from django.urls import path, include
from . import views

urlpatterns = [
    path('webhook/',views.webhook_view, name='webhook'),
    path('webhook/progress/',views.webhook_progress, name='webhook_progress'),
]