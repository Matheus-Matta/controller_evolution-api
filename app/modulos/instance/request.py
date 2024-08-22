import requests
from django.conf import settings

def instance_delete(instance):
    response = requests.delete (
            f"https://api.star.dev.br/instance/delete/{instance.name}",
            headers={"apikey": instance.token })
    return response

def instance_logout(instance):
    response = requests.delete( 
        f"https://api.star.dev.br/instance/logout/{instance.name}",
        headers={ "apikey": instance.token })
    return response

def instance_connect(instance):
    response = requests.get(
         f"https://api.star.dev.br/instance/connect/{instance.name}",
         headers={"apikey":instance.token})
    return response

def instance_restart(instance):
    response = requests.put(
         f"https://api.star.dev.br/instance/restart/{instance.name}",
         headers={"apikey":instance.token})
    return response

def instance_create(instance):
    data = {
                "instanceName": instance.name,
                "token": instance.token if instance.token else "",
                "qrcode": True,
                "integration": f"WHATSAPP-{instance.integration_type.upper()}"
            }  

    response = requests.post("https://api.star.dev.br/instance/create", json=data, 
                    headers={"Content-Type": "application/json", "apikey": settings.GLOBAL_TOKEN_EVOLUTION }
                )
    return response