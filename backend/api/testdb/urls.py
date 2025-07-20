from django.urls import path
from . import views

urlpatterns =[
    path('backendDB/', views.Db.as_view())
]