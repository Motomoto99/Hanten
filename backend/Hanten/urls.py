"""
URL configuration for Hanten project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.http import JsonResponse
import os
from channels.layers import get_channel_layer
import asyncio
from clerk_django.client import ClerkClient

def health_check(request):
    import redis

    redis_url = os.environ.get("REDIS_URL")
    redis_status = "Not Configured"
    redis_connection_ok = False

    if redis_url:
        try:
            # 実際にRedisに接続を試みる
            r = redis.from_url(redis_url)
            r.ping()
            redis_status = "OK"
            redis_connection_ok = True
        except Exception as e:
            redis_status = f"Failed: {str(e)}"
    
    return JsonResponse({
        "django_status": "OK",
        "redis_status": redis_status,
        "redis_connection_ok": redis_connection_ok,
    })

def auth_test(request):
    try:
        # ヘッダーから、テスト用のトークンを取り出す
        auth_header = request.headers.get('Authorization')
        if not auth_header or 'Bearer ' not in auth_header:
            return JsonResponse({"status": "error", "message": "Authorization header missing or invalid"}, status=401)
        
        token = auth_header.split(' ')[1]
        
        clerk_client = ClerkClient(secret_key=os.environ.get("CLERK_SECRET_KEY"))
        payload = clerk_client.verify_token(token)
        
        # 成功すれば、勝利のメッセージを返す
        return JsonResponse({"status": "ok", "user_id": payload.get('id')})

    except Exception as e:
        # 失敗すれば、その理由を正直に白状させる
        return JsonResponse({"status": "error", "message": str(e)}, status=500)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/testapi/', include('api.testapi.urls')),
    path('api/testdb/', include('api.testdb.urls')),
    path('api/user/', include('api.user.urls')),
    path('api/webhook/', include('api.webhook.urls')),
    path('api/debate/', include('api.debate.urls')),
    # path('api/messaging/', include('api.messaging.urls')),
    path('health/', health_check, name='health_check'),
    path('auth-test/', auth_test, name='auth_test'), 
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)