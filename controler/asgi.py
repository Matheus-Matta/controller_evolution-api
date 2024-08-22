import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import app.modulos.webhook.routing

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'controler.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            app.modulos.webhook.routing.websocket_urlpatterns
        )
    ),
})
