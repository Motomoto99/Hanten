from rest_framework import serializers
from .models import Theme, Room,User,Participate,Comment
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
    is_participating = serializers.BooleanField(read_only=True) # ユーザーが参加しているかどうか

    class Meta:
        model = Room
        fields = ['id', 'room_name', 'room_start', 'room_end', 'theme_title', 'participant_count', 'is_participating']

class RoomDetailSerializer(serializers.ModelSerializer):
    """詳細表示用のシリアライザー"""
    theme = ThemeSerializer(read_only=True)
    creator = UserSerializer(read_only=True) #これはいるかな？
    is_participating = serializers.SerializerMethodField()
    user_participation = serializers.SerializerMethodField() 

    class Meta:
        model = Room
        fields = '__all__'
        extra_fields = ['is_participating']

    def get_is_participating(self, obj):
        """
        リクエストを送ってきたユーザーが、この部屋(obj)に参加しているかを判定する
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'clerk_user'):
            return False
        
        clerk_user_id = request.clerk_user.get('id')
        if not clerk_user_id:
            return False
            
        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
            return Participate.objects.filter(room=obj, user=user).exists()
        except User.DoesNotExist:
            return False
    
    def get_user_participation(self, obj):
        """
        リクエストを送ってきたユーザーの、この部屋(obj)への参加情報を返す
        """
        request = self.context.get('request')
        if not request or not hasattr(request, 'clerk_user'):
            return None
            
        clerk_user_id = request.clerk_user.get('id')
        if not clerk_user_id:
            return None

        try:
            user = User.objects.get(clerk_user_id=clerk_user_id)
            participation = Participate.objects.get(room=obj, user=user)
            return ParticipateSerializer(participation).data
        except (User.DoesNotExist, Participate.DoesNotExist):
            return None

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

class ParticipateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Participate
        fields = ['position'] # とりあえず立場(position)だけ返す

class CommentSerializer(serializers.ModelSerializer):
    # senderはユーザーIDだけでなく、ユーザー名なども含めて返す
    sender = UserSerializer(read_only=True, source='user')

    class Meta:
        model = Comment
        fields = ['id', 'comment_text', 'post_date', 'sender']