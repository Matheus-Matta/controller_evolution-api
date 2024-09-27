
from django.urls import path, include
from . import views
from .api import *

urlpatterns = [
    path('campaign', views.campaign, name='campaign'),
    path('campaign/progress/<str:task_id>', views.campaign_progress, name='campaign_progress'),
    path('campaign/progress/exit/<str:campaign_id>', views.encerrar_campaign, name='encerrar_campaign'),

    path('api/campaigns', list_campaign, name='list_campaign'),
    path('api/campaigns/<int:campaign_id>', campaign_details, name='campaign_details'),
    path('api/campaigns/exit/<int:campaign_id>', campaign_encerrar, name='campaign_encerrar'),
    path('api/campaigns/add/<str:instance_name>', campaign_add_response, name='campaign_add_response'),
    path('api/campaigns/del/<int:campaign_id>', campaign_delete, name='campaign_delete'),
  
]