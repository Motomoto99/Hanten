from django.shortcuts import render

from rest_framework import generics
from .models import Room
from .serializers import RoomListSerializer, RoomDetailSerializer
from django.db.models import Count # Countをインポート
# from api.permissions.clerk import ClerkAuthenticated

class DebateListAPIView(generics.ListAPIView):
    """
    ディベート部屋の一覧を取得するAPI
    """
    queryset = Room.objects.select_related('theme').annotate( 
        participant_count=Count('participants') # 参加者数をカウントするためのアノテーション
    ).order_by('-room_start') # 最新のディベート部屋が先頭に来るように並び替え
    serializer_class = RoomListSerializer
    # permission_classes = [ClerkAuthenticated] # ログインユーザーのみアクセス可

class DebateDetailAPIView(generics.RetrieveAPIView):
    """
    個別のディベート部屋の詳細を取得するAPI
    """
    queryset = Room.objects.select_related('theme', 'creator')
    serializer_class = RoomDetailSerializer
    # permission_classes = [ClerkAuthenticated]

