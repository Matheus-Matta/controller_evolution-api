
from django.urls import path, include
from . import views
from .api import list_campaign, campaign_details,campaign_encerrar

urlpatterns = [
    path('campaign', views.campaign, name='campaign'),
    path('campaign/progress/<str:task_id>', views.campaign_progress, name='campaign_progress'),
    path('campaign/progress/exit/<str:campaign_id>', views.encerrar_campaign, name='encerrar_campaign'),

    path('api/campaigns', list_campaign, name='list_campaign'),
    path('api/campaigns/<int:campaign_id>', campaign_details, name='campaign_details'),
    path('api/campaigns/exit/<int:campaign_id>', campaign_encerrar, name='campaign_encerrar'),
  
]