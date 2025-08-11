from django.shortcuts import render

from rest_framework import generics, status
from .models import Room
from .serializers import RoomListSerializer, RoomDetailSerializer,RoomCreateSerializer
from django.db.models import Count # Countをインポート
from api.pagination import StandardResultsSetPagination # 作成したページネーションをインポート
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from .models import Room, Theme, User
from .serializers import RoomListSerializer, RoomDetailSerializer, ThemeSerializer
# from api.permissions.clerk import ClerkAuthenticated

class DebateListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RoomListSerializer
    # permission_classes = [ClerkAuthenticated]
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        """
        URLのクエリパラメータに応じて、開催中か終了済みかをフィルタリングする
        """
        queryset = Room.objects.select_related('theme').annotate(
            participant_count=Count('participate', distinct=True) # distinct=Trueで重複カウントを防止
        ).order_by('-room_start')
        # 代わりに、エラーの起きないシンプルな queryset を一時的に設定
        # queryset = Room.objects.all().order_by('-room_start')

        status = self.request.query_params.get('status', 'ongoing')
        now = timezone.now()

        if status == 'ongoing':
            return queryset.filter(room_end__gt=now)
        elif status == 'finished':
            return queryset.filter(room_end__lte=now)
        
        return queryset

    def get_serializer_class(self):
        """
        リクエストのメソッドに応じて、使用するシリアライザーを切り替える
        """
        if self.request.method == 'POST':
            return RoomCreateSerializer
        return RoomListSerializer

    def perform_create(self, serializer):
        """
        POSTリクエストで部屋を作成する際の追加ロジック
        """
        serializer.save()

# 参加者数をカウントして、レスポンスに含める
class ThemeListAPIView(generics.ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

class DebateDetailAPIView(generics.RetrieveAPIView):
    """
    個別のディベート部屋の詳細を取得するAPI
    """
    queryset = Room.objects.select_related('theme', 'creator')
    serializer_class = RoomDetailSerializer
    # permission_classes = [ClerkAuthenticated]

