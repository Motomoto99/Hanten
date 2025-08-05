from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from svix.webhooks import Webhook, WebhookVerificationError
from api.user.models import User  # usersアプリのモデルをインポート
import os

# Create your views here.
class Clerk(APIView):
    # Clerkからの通信なので、CSRF保護などは不要
    authentication_classes = []
    permission_classes = []

    def post(self, request):
        # Clerkダッシュボードで設定したWebhookの秘密鍵を取得
        WEBHOOK_SECRET = os.environ.get('CLERK_WEBHOOK_SECRET')
        if not WEBHOOK_SECRET:
            return Response({"error": "Webhookシークレットが設定されていません"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        # ヘッダーから署名情報を取得
        headers = request.headers
        svix_id = headers.get('svix-id')
        svix_timestamp = headers.get('svix-timestamp')
        svix_signature = headers.get('svix-signature')

        if not all([svix_id, svix_timestamp, svix_signature]):
            return Response({"error": "ヘッダー情報が不足しています"}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # 署名を検証して、本当にClerkからの通信か確認する
            wh = Webhook(WEBHOOK_SECRET)
            payload = wh.verify(request.body, headers)
        except WebhookVerificationError:
            return Response({"error": "Webhookの署名検証に失敗しました"}, status=status.HTTP_400_BAD_REQUEST)
        
        event_type = payload['type']

        # 新規ユーザーが作成されたイベントの場合
        if event_type == 'user.created':
            data = payload['data']
            clerk_user_id = data['id']
            
            # DBに同じユーザーがいなければ、作成する
            if not User.objects.filter(clerk_user_id=clerk_user_id).exists():
                User.objects.create(
                    clerk_user_id=clerk_user_id,
                    # 最初は仮のユーザー名を入れておく
                    user_name=f"user_{clerk_user_id[:8]}" 
                )
        
        return Response(status=status.HTTP_200_OK)