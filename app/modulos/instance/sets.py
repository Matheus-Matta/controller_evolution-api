import requests
from django.conf import settings

def setWebwook(instance_name, instance_token):
    response = requests.post(f"https://api.star.dev.br/webhook/set/{instance_name}",
                    json={
                        "url": f"{settings.BASE_URL}/webhook/",
                        "webhook_by_events": False,
                        "events": [
                            "APPLICATION_STARTUP","QRCODE_UPDATED","MESSAGES_SET",
                            "MESSAGES_UPSERT","MESSAGES_UPDATE","MESSAGES_DELETE",
                            "SEND_MESSAGE","CONTACTS_SET","CONTACTS_UPSERT",
                            "CONTACTS_UPDATE","PRESENCE_UPDATE","CHATS_SET",
                            "CHATS_UPSERT","CHATS_UPDATE","CHATS_DELETE",
                            "GROUPS_UPSERT","GROUP_UPDATE","GROUP_PARTICIPANTS_UPDATE",
                            "CONNECTION_UPDATE","CALL","NEW_JWT_TOKEN",
                            "TYPEBOT_START","TYPEBOT_CHANGE_STATUS",
                        ]     
                    }, 
                    headers={"Content-Type": "application/json", "apikey": instance_token }
                )
    
    return response