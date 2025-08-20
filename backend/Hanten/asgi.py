import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hanten.settings')

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator # ★★★ 信頼できる訪問者リストをチェックする執事をインポート ★★★
import api.debate.routing # これから作成するルーティングファイルをインポート
# from clerk_django.middlewares.websockets import ClerkAsyncAuthMiddleware 見つからない

application = ProtocolTypeRouter({
    # ★★★ 普通の訪問者は、Djangoの正規の入口へ ★★★
    "http": get_asgi_application(),
    # ★★★ 特別な訪問者（WebSocket）は、まず執事（AllowedHostsOriginValidator）がチェックし、
    # その後、専用の入口（URLRouter）へ案内する ★★★
    "websocket": AllowedHostsOriginValidator(
        URLRouter(
            api.debate.routing.websocket_urlpatterns
        )
    ),
})