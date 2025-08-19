import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hanten.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
import api.debate.routing # これから作成するルーティングファイルをインポート


application = ProtocolTypeRouter({
    # ★★★ 普通の訪問者は、Djangoの正規の入口へ ★★★
    "http": django_asgi_app,
    # ★★★ 特別な訪問者（WebSocket）は、まず執事（AllowedHostsOriginValidator）がチェックし、
    # その後、専用の入口（URLRouter）へ案内する ★★★
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            api.debate.routing.websocket_urlpatterns
        )
    ),
})