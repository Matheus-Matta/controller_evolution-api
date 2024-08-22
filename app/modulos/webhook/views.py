from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from app.modulos.instance.models import Instance
from app.modulos.contact.utils import create_contact

@csrf_exempt
def webhook_view(request):
    if request.method == 'POST':
        try:
            event = json.loads(request.body)
            apikey = event.get('apikey')
            if event.get('event') == 'connection.update' and event.get('data', {}).get('state') == 'open':
                number = event.get('sender')
                if number and apikey:
                    try:
                        instance = Instance.objects.get(token=apikey)
                        instance.number = number.replace('@s.whatsapp.net', '')
                        instance.save()
                        print(f"Numero {number} foi adicionado para a instância {instance.name}")
                    except Instance.DoesNotExist:
                        print(f"Instância com apikey {apikey} não encontrada.")

            if event.get('event') == 'contacts.upsert':
                number = event.get('sender')
                try:
                    instance = Instance.objects.get(token=apikey)
                    contacts = event.get('data', [])
                    for contact in contacts:
                        number = contact.get('id').replace('@s.whatsapp.net', '')
                        name = contact.get('pushName')
                        if name and number:
                            create_contact(instance, instance.user, name, number, [f'whatsapp_{instance.public_name}'])
                       
                except Instance.DoesNotExist:
                    print(f"Instância com apikey {apikey} não encontrada.")

            if event.get('event') == "contacts.update":
                try:
                    instance = Instance.objects.get(token=apikey)
                    contacts = event.get('data', [])
                    for contact in contacts:
                        number = contact.get('id').replace('@s.whatsapp.net', '')
                        name = contact.get('pushName')
                        if name and number:
                            create_contact(instance, instance.user, name, number, [f'whatsapp_{instance.name}'])
                except Instance.DoesNotExist:
                    print(f"Instância com apikey {apikey} não encontrada.")
                
           
            try:
                instance = Instance.objects.get(token=apikey)
                user_id = instance.user.id
            except Instance.DoesNotExist:
                print(f"Instância com apikey {apikey} não encontrada.")
                return JsonResponse({'status': 'error', 'message': 'Instance not found'}, status=404)

            # Envia o evento para o grupo do usuário
            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                f'webhook_{user_id}',
                {
                    'type': 'webhook_message',
                    'message': event
                }
            )

            return JsonResponse({'status': 'success'})
        except Exception as e:
            print('Erro ao processar webhook:', str(e))
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

    return JsonResponse({'status': 'invalid method'}, status=405)