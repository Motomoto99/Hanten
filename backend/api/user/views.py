from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User
from .serializers import UserSerializer

# Create your views here.
class Me(APIView):
    """
    ログイン中のユーザー情報を取得する
    """
    def get(self, request): #GETリクエストの場合かな
        # Clerkが認証したユーザーIDを取得
        clerk_user_id = request.clerk_user.get('id')
        if not clerk_user_id:
            return Response({"error": "認証されていません"}, status=401)
        
        try:
            # Clerk IDを元に、データベースから自分のユーザー情報を探す
            user = User.objects.get(clerk_user_id=clerk_user_id)
            serializer = UserSerializer(user)
            # フロントエンドに、綺麗なJSONで情報を返す
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが見つかりません"}, status=404)

    # """
    # 初回ログイン時のプロフィール情報を更新する
    # """
    # put(self, request):
    #     """
    #     初回ログイン時のプロフィール情報を更新する
    #     """
    #     clerk_user_id = request.auth.get('user_id')
    #     if not clerk_user_id:
    #         return Response({"error": "認証されていません"}, status=status.HTTP_401_UNAUTHORIZED)

    #     try:
    #         user = User.objects.get(clerk_user_id=clerk_user_id)
            
    #         # フロントエンドから送られてきた新しいユーザー名で更新
    #         user.user_name = request.data.get('user_name', user.user_name)
    #         # 初回フラグをFalseにする
    #         user.first_flag = False
    #         user.save()

    #         serializer = UserSerializer(user)
    #         return Response(serializer.data)
    #     except User.DoesNotExist:
    #         return Response({"error": "ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)