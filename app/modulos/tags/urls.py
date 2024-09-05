from django.urls import path, include
from . import views

urlpatterns = [

    path('contact/create_tag',views.create_tag,name='create_tag'),
    path('contact/add_tags_to_contacts',views.add_tags_to_contacts,name='add_tags_to_contacts'),
    path('tag/delete', views.delete_tag, name='delete_tag'),
]