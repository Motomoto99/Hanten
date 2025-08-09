from django.urls import path
from . import views

urlpatterns = [
    path('debates/', views.DebateListAPIView.as_view(), name='debate-list'),
    path('debates/<int:pk>/', views.DebateDetailAPIView.as_view(), name='debate-detail'),
]