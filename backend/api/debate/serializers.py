from rest_framework import serializers
from .models import Theme, Room
from api.user.serializers import UserSerializer
from django.db.models import Count # Countをインポート

class ThemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Theme
        fields = '__all__'

class RoomListSerializer(serializers.ModelSerializer):
    """一覧表示用のシリアライザー"""
    theme_title = serializers.CharField(source='theme.theme_title', read_only=True)
    participant_count = serializers.IntegerField(read_only=True) # 参加者数

    class Meta:
        model = Room
        fields = ['id', 'room_name', 'room_start', 'room_end', 'theme_title', 'participant_count']

class RoomDetailSerializer(serializers.ModelSerializer):
    """詳細表示用のシリアライザー"""
    theme = ThemeSerializer(read_only=True)
    creator = UserSerializer(read_only=True) #これはいるかな？

    class Meta:
        model = Room
        fields = '__all__'