import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hanten.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator # ★★★ 信頼できる訪問者リストをチェックする執事をインポート ★★★
import api.debate.routing # これから作成するルーティングファイルをインポート
from clerk_django.middlewares.websockets import ClerkAsyncAuthMiddleware

class DebuggingMiddleware:
    """
    すべての通信リクエストの情報をログに出力する、デバッグ用のミドルウェア
    """
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        # scope['type']で、httpかwebsocketかを見分ける
        if scope['type'] == 'websocket':
            print("\n--- [ASGI DEBUG] WebSocket接続リクエストを検知！ ---")
        else:
            print("\n--- [ASGI DEBUG] HTTPリクエストを検知！ ---")
        
        # ヘッダー情報など、scopeの中身を詳しく表示
        for key, value in scope.items():
            print(f"{key}: {value}")
        print("--------------------------------------------------\n")

        # 確認が終わったら、本来のアプリに処理を渡す
        return await self.app(scope, receive, send)

application = ProtocolTypeRouter({
    # ★★★ 普通の訪問者は、Djangoの正規の入口へ ★★★
    "http": django_asgi_app,
    # ★★★ 特別な訪問者（WebSocket）は、まず執事（AllowedHostsOriginValidator）がチェックし、
    # その後、専用の入口（URLRouter）へ案内する ★★★
    "websocket": ClerkAsyncAuthMiddleware(
        URLRouter(
            api.debate.routing.websocket_urlpatterns
        )
    ),
})