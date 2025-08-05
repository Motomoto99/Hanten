from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.Me.as_view()),
    # path('me/created_debates/', views.Created.as_view()), #ユーザーが作成したディベート一覧
    # path('me/participate_debates', views.Participate.as_view()) #ユーザーが参加中または参加したディベート一覧
    #機能へのパスを指定する、viewsファイルのBackendクラスを指定している
]