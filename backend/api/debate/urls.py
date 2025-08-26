from django.urls import path
from . import views

urlpatterns = [
    path('debates/', views.DebateListCreateAPIView.as_view(), name='debate-list-create'),
    path('debates/<int:pk>/', views.DebateDetailAPIView.as_view(), name='debate-detail'),
    path('themes/', views.ThemeListAPIView.as_view(), name='theme-list'),
    path('debates/<int:pk>/messages/', views.MessageListAPIView.as_view(), name='message-list'),
    path('debates/<int:pk>/messages/post', views.FirstMessageAPIView.as_view(), name='first-message'),
    path('debates/<int:pk>/read_status/', views.ReadStatusUpdateAPIView.as_view(), name='read-status-update'),
    path('debates/<int:pk>/feedback/', views.AIFeedbackView.as_view(), name='ai-feedback'),
]