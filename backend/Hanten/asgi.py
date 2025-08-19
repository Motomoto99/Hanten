import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Hanten.settings')
django_asgi_app = get_asgi_application()

from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator # ★★★ 信頼できる訪問者リストをチェックする執事をインポート ★★★
from channels.auth import AuthMiddlewareStack 
import api.debate.routing # これから作成するルーティングファイルをインポート

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
    "http": django_asgi_app,
    
    # ★★★ Clerkの門番を解任し、より柔軟なAuthMiddlewareStackに戻します ★★★
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                api.debate.routing.websocket_urlpatterns
            )
        )
    ),
})