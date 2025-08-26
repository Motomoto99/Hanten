from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    ユーザーモデルをJSONに変換するためのシリアライザー
    """
    class Meta:
        model = User
        # フロントエンドに渡したいフィールドだけをここに書きます
        fields = '__all__'

class DebateEvaluationSerializer(serializers.Serializer):
    """
    ディベート評価画面用のデータをまとめる、特別なシリアライザー
    """
    # ユーザー個人の成績
    my_comment_count = serializers.IntegerField()
    my_comment_percentage = serializers.FloatField()
    
    # ディベート全体の状況
    total_comment_count = serializers.IntegerField()
    agree_percentage = serializers.FloatField()
    disagree_percentage = serializers.FloatField()

class UserProfileSerializer(serializers.ModelSerializer):
    """
    ユーザープロフィール画面用の、特別なシリアライザー
    """
    # 参加したディベートの数を、ここに追加します
    participated_count = serializers.IntegerField()

    class Meta:
        model = User
        # 必要な情報だけを、厳選して渡します
        fields = ['user_name', 'participated_count']