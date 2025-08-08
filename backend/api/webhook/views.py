from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from svix.webhooks import Webhook, WebhookVerificationError
from api.user.models import User  # usersアプリのモデルをインポート
import os
import json
from django.utils import timezone

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
            clerk_user_id = data.get('id')
            # メールアドレスも取得する
            email_address = data.get('email_addresses', [{}])[0].get('email_address')

            if not all([clerk_user_id, email_address]):
                return Response({"error": "IDまたはメールアドレスが不足しています"}, status=status.HTTP_400_BAD_REQUEST)

            try:
                # まず、メールアドレスで既存ユーザーを探す
                user = User.objects.get(email=email_address)
                print('ユーザー情報を更新します:', clerk_user_id,user.clerk_user_id)
                # 見つかった -> 復帰処理
                user.clerk_user_id = clerk_user_id # 新しいClerk IDに更新
                user.user_name = clerk_user_id  # 仮のユーザー名を設定
                user.deleted_date = None          # 退会日を消去
                user.first_flag = True            # もう一度初回ログイン扱いに
                user.save()

            except User.DoesNotExist:
                # 見つからなかった -> 本当の新規登録
                User.objects.create(
                    clerk_user_id=clerk_user_id,
                    email=email_address,
                    user_name=clerk_user_id # 仮のユーザー名
                )
                

        
        # ユーザーが削除された場合
        elif event_type == 'user.deleted':
            data = payload['data']
            clerk_user_id = data.get('id')
            print("受診を受け取り処理開始")

            # Clerk IDがちゃんと存在するか確認
            if not clerk_user_id:
                return Response({"error": "ClerkユーザーIDがペイロードに含まれていません"}, status=status.HTTP_400_BAD_REQUEST)

            # DBから該当するユーザーを探す
            try:
                print("ユーザー削除イベントを受信: ID =", clerk_user_id)
                user_to_delete = User.objects.get(clerk_user_id=clerk_user_id)
                
                # ユーザーをDBから完全に消すのではなく、「退会日時」に今の時刻を入れる（ソフトデリート）
                if user_to_delete.deleted_date is None:
                    print("ユーザーをソフトデリート: ID =", clerk_user_id)
                    user_to_delete.deleted_date = timezone.now()
                    user_to_delete.save()

            except User.DoesNotExist:
                # もしDBに該当ユーザーがいなくても、エラーにはせず、静かに終了する
                print("ユーザーが見つかりませんでした: ID =", clerk_user_id)
                pass
        
        return Response(status=status.HTTP_200_OK)