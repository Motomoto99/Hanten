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
from django.http import JsonResponse
from django.conf import settings
from django.conf.urls.static import static


import os
from channels.layers import get_channel_layer
import asyncio

from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from api.permissions.clerk import ClerkAuthenticated

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

@api_view(['GET'])
@permission_classes([ClerkAuthenticated]) # ← Clerkの門番が仕事をした後、この許可証でチェックする
def auth_test(request):
    # この関数にたどり着けた、ということは、認証は成功している！
    user_id = request.clerk_user.get('id')
    return JsonResponse({"status": "ok", "message": "おめでとうございます！認証は完璧です！", "user_id": user_id})

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