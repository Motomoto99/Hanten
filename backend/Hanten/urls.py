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
import redis

def health_check(request):
    redis_url = os.environ.get("REDIS_URL")
    redis_status = "Not Configured"
    redis_connection_ok = False
    if redis_url:
        try:
            # 実際にRedisに接続を試みる！
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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/testapi/', include('api.testapi.urls')),
    path('api/testdb/', include('api.testdb.urls')),
    path('api/user/', include('api.user.urls')),
    path('api/webhook/', include('api.webhook.urls')),
    path('api/debate/', include('api.debate.urls')),
    # path('api/messaging/', include('api.messaging.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)