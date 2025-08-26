from django.urls import path
from . import views

urlpatterns = [
    path('me/', views.Me.as_view(), name='me'),
    # path('me/created_debates/', views.Created.as_view()), #ユーザーが作成したディベート一覧
    path('me/participate_debates/', views.ParticipatedDebateListView.as_view(), name='participate-debates'),
    path('me/<int:debateId>/evaluation/', views.DebateEvaluationView.as_view(), name='debate-evaluation'),
]