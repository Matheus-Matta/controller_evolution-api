from django.urls import path, include
from . import views

urlpatterns = [

    path('contacts',views.contact,name="contact"),
    path('contact/create',views.contact_create,name="contact_create"),
    path('contact/update',views.update_contact,name="update_contact"),
    path('contact/delete',views.delete_contacts,name='delete_contacts'),
    path("contact/import",views.import_contact,name='import_contact'),
    path('contact/filter-contacts',views.filter_contact_by_name, name='filter_contact_by_name'),
]