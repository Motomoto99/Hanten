from rest_framework import serializers
from .models import Theme, Room,User
from api.user.serializers import UserSerializer
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta

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

class RoomCreateSerializer(serializers.ModelSerializer):
    duration_hours = serializers.IntegerField(write_only=True, min_value=1)
    theme_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Room
        fields = ['id', 'room_name', 'duration_hours', 'theme_id']
        read_only_fields = ['id']

    def create(self, validated_data):
        duration_hours = validated_data.pop('duration_hours')
        theme_id = validated_data.pop('theme_id')
        
        request = self.context['request']
        # clerk_userはミドルウェアによって保証されている
        clerk_user_id = request.clerk_user.get('id') 
        
        try:
            # Clerk IDを元に、DBから正しい「User」インスタンスを取得
            creator = User.objects.get(clerk_user_id=clerk_user_id)
        except User.DoesNotExist:
            raise serializers.ValidationError("Authenticated user does not exist in the database.")

        end_time = timezone.now() + timedelta(hours=duration_hours)

        room = Room.objects.create(
            creator=creator,
            theme_id=theme_id,
            room_end=end_time,
            **validated_data
        )
        return room