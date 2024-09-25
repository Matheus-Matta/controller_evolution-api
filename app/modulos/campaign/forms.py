from django import forms
from .models import Campaign
from app.modulos.instance.models import Instance 

class CampaignForm(forms.ModelForm):
    
    # campo para por o nome ve
    name = forms.CharField(
        label="nome da campanha",
        max_length=255, 
        required=True
    )
    # Campo de número inicial para o envio das mensagens
    start_number = forms.IntegerField(
        label="Enviar a partir",
        min_value=1,  # Começar do primeiro número
        required=True
    )

    # Campo de número final para o envio das mensagens
    end_number = forms.IntegerField(
        label="Enviar até",
        min_value=1,  # O número mínimo é 1
        required=True
    )

    end_timeout = forms.IntegerField(
        label="final do intervalo",
        min_value=1,  # O número mínimo é 1
        required=True
    )

    start_timeout = forms.IntegerField(
        label="inicio do intervalo",
        min_value=1,  # O número mínimo é 1
        required=True
    )

    # Novo campo: checkbox para pausas entre mensagens
    enable_pause = forms.BooleanField(
        label="Pausas entre mensagens",
        required=False
    )

    # Campos adicionais (mínimo e máximo pausa, e quantidade de pausas)
    min_pause = forms.IntegerField(
        label="Mínimo",
        min_value=1,
        required=False  # Será exibido apenas se 'enable_pause' for True
    )

    max_pause = forms.IntegerField(
        label="Máximo",
        min_value=1,
        required=False  # Será exibido apenas se 'enable_pause' for True
    )

    pause_quantity = forms.IntegerField(
        label="Quantidades",
        min_value=1,
        required=False  # Será exibido apenas se 'enable_pause' for True
    )

    # Campo de saudação (checkbox)
    send_greeting = forms.BooleanField(
        label="Enviar mensagem de saudação",
        required=False
    )


    instance = forms.ModelMultipleChoiceField(
            queryset=Instance.objects.none(),  # Será filtrado no __init__
            label="Escolha as instâncias",
            widget=forms.CheckboxSelectMultiple,  # Usar checkboxes em vez de múltipla seleção
            required=True
    )

    class Meta:
        model = Campaign
        fields = [
            'name','start_number','end_number',
            'start_timeout', 'end_timeout', 'enable_pause',
            'min_pause', 'max_pause', 'pause_quantity',
            'send_greeting', 'instance'
        ]

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Recebe o usuário no init
        super(CampaignForm, self).__init__(*args, **kwargs)

        # Filtrar instâncias que pertencem ao usuário
        if user:
            self.fields['instance'].queryset = Instance.objects.filter(user=user)

    def clean(self):
        cleaned_data = super().clean()
        start_number = cleaned_data.get('start_number')
        end_number = cleaned_data.get('end_number')

        # Validação para verificar se o número final é maior que o inicial
        if start_number and end_number and start_number > end_number:
            self.add_error('end_number', "O número final deve ser maior que o número inicial.")
        
        # Validação adicional se o checkbox de pausa estiver marcado
        enable_pause = cleaned_data.get('enable_pause')
        min_pause = cleaned_data.get('min_pause')
        max_pause = cleaned_data.get('max_pause')
        pause_quantity = cleaned_data.get('pause_quantity')

        if enable_pause:
            if not min_pause or not max_pause or not pause_quantity:
                self.add_error('min_pause', "Todos os campos de pausa são obrigatórios se 'Pausas entre mensagens' estiver marcado.")
            if min_pause and max_pause and min_pause > max_pause:
                self.add_error('max_pause', "O valor máximo da pausa deve ser maior que o valor mínimo.")

        return cleaned_data