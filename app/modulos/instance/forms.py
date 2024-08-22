from django import forms
from django.utils.translation import gettext_lazy as _
from .models import Instance
    
class InstanceForm(forms.ModelForm):
    class Meta:
        model = Instance
        fields = ['name', 'integration_type', 'token', 'number']
        widgets = {
            'token': forms.TextInput(attrs={'placeholder': 'Digite o token de integração (opcional)'}),
            'number': forms.TextInput(attrs={'placeholder': 'Digite o número (opcional)'}),
        }