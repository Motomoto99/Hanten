from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    """
    ユーザーモデルをJSONに変換するためのシリアライザー
    """
    class Meta:
        model = User
        # フロントエンドに渡したいフィールドだけをここに書きます
        fields = [__all__]