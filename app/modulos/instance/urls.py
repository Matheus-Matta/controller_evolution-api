
from django.urls import path
from . import views

urlpatterns = [
  
    path('create_instacia',views.create_instancia,name="create_instancia"),
    path('instance/delete', views.delete_instance, name='delete_instance'),
    path('instance/connect', views.connect_instance, name='connect_instance'),
    path('instance/restart', views.restart_instance, name='restart_instance'),
    path('instance/logout', views.logout_instance, name='logout_instance'),
    path('instance/<int:id>', views.instance_detail, name='instance_detail'),
    

]