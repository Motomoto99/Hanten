from django.urls import path
from . import views

urlpatterns = [
    path('debates/', views.DebateListCreateAPIView.as_view(), name='debate-list-create'),
    path('debates/<int:pk>/', views.DebateDetailAPIView.as_view(), name='debate-detail'),
    path('themes/', views.ThemeListAPIView.as_view(), name='theme-list'),
]