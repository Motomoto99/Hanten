import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.debate.routing # これから作成するルーティングファイルをインポート

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hanten.settings')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            api.debate.routing.websocket_urlpatterns
        )
    ),
})