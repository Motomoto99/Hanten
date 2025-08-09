from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import User
from .serializers import UserSerializer

# Create your views here.
class Me(APIView):
    """
    ログイン中のユーザー情報を取得する
    """
    def get(self, request): #GETリクエストの場合かな
        print("--- /api/user/me/ GETリクエスト受信 ---")
        # Clerkが認証したユーザーIDを取得
        clerk_user_id = request.clerk_user.get('id')
        if not clerk_user_id:
            print("[ERROR] 環境変数 'CLERK_SECRET_KEY' が設定されていません！")
            return Response({"error": "認証されていません"}, status=401)

        #ClerkのWebhookはより先にこっちでユーザーを探しても見つからないからここで検索して見つからなかったら登録する
        # try:
        #     # まず、メールアドレスで既存ユーザーを探す
        #     user = User.objects.get(email=email_address)
                
        #     # 見つかった -> 復帰処理
        #     user.clerk_user_id = clerk_user_id # 新しいClerk IDに更新
        #     user.deleted_date = None          # 退会日を消去
        #     user.first_flag = True            # もう一度初回ログイン扱いに
        #     user.save()

        # except User.DoesNotExist:
        #     # 見つからなかった -> 本当の新規登録
        #     User.objects.create(
        #         clerk_user_id=clerk_user_id,
        #         email=email_address,
        #         user_name=clerk_user_id # 仮のユーザー名
        #     )

        try:
            print("IDを基にユーザー情報を取得開始...",clerk_user_id)
            # Clerk IDを元に、データベースから自分のユーザー情報を探す
            user = User.objects.get(clerk_user_id=clerk_user_id)
            serializer = UserSerializer(user)
            # フロントエンドに、綺麗なJSONで情報を返す
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが見つかりません"}, status=404)

    """
    初回ログイン時のプロフィール情報を更新する
    """
    def put(self, request):
        clerk_user_id = request.clerk_user.get('id')
        if not clerk_user_id:
            return Response({"error": "認証されていません"}, status=status.HTTP_401_UNAUTHORIZED)

        # Clerk IDを元に、更新対象のユーザーを取得
        try:
            print("IDを基にユーザー情報を取得開始...", clerk_user_id)
            user = User.objects.get(clerk_user_id=clerk_user_id)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)

        # フロントエンドから送られてきた新しいユーザー名を取得
        new_user_name = request.data.get('user_name')
        if not new_user_name:
            return Response({"error": "ユーザー名が指定されていません"}, status=status.HTTP_400_BAD_REQUEST)
        
        print('/user/me/のPUTリクエスト受信:', clerk_user_id, new_user_name)
        # ユーザー名と初回フラグを更新
        user.user_name = new_user_name
        user.first_flag = False
        user.save()

        return Response(status=status.HTTP_200_OK)
