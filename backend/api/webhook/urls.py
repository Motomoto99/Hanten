from django.urls import path
from . import views

urlpatterns = [
    path('clerk/', views.Clerk.as_view()) 
    #機能へのパスを指定する、viewsファイルのClerkクラスを指定している
]