# backend/api/debate/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from clerk_django.client import ClerkClient
import os

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print("\n--- [CONNECT] WebSocket接続試行を検知 ---")
        try:
            query_string = self.scope['query_string'].decode()
            print(f"[CONNECT] クエリ文字列: {query_string}")

            if 'token=' not in query_string:
                print("[ERROR] クエリに 'token' が見つかりません。")
                await self.close()
                return

            token = [p.split('=')[1] for p in query_string.split('&') if p.startswith('token=')][0]
            print("[CONNECT] トークンの抽出に成功。Clerkに検証を依頼します...")

            clerk_client = ClerkClient()
            payload = clerk_client.verify_token(token)

            self.scope['clerk_user'] = payload
            print(f"[SUCCESS] WebSocket 認証成功: user_id={payload.get('id')}")

        except Exception as e:
            print(f"[FATAL] WebSocket 認証中に致命的なエラー: {e}")
            await self.close()
            return
        
        # 認証成功後、グループに参加
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'
        
        print(f"[CONNECT] Redisグループ ({self.room_group_name}) に参加します...")
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        print("[SUCCESS] Redisグループへの参加完了。")

        await self.accept()
        print("--- [SUCCESS] WebSocket接続を完全に確立しました ---")

    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # WebSocketでメッセージを受信
    async def receive(self, text_data):
        # ★★★ 空のデータが来たら、何もしないで無視する ★★★
        if not text_data:
            return

        try:
            data = json.loads(text_data)
        except json.JSONDecodeError:
            # ★★★ JSONとして読めないデータも、無視する ★★★
            return
            
        clerk_user_id = self.scope['clerk_user'].get('sub')
        message_content = json.loads(text_data).get('message')

        if not all([message_content, clerk_user_id]):
            return

        # DBにメッセージを保存
        new_message = await self.save_message(message_content, clerk_user_id)

        # グループ内の全員にメッセージを送信
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': new_message
            }
        )
    
    # グループからメッセージを受信してWebSocketに送信
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def save_message(self, content, clerk_user_id):
        from .models import Room, Comment, User, Participate
        from .serializers import CommentSerializer

        sender = User.objects.get(clerk_user_id=clerk_user_id)
        room = Room.objects.get(id=self.room_id)
        comment = Comment.objects.create(room=room, user=sender, comment_text=content)
        
        # シリアライザを使ってコメントをシリアライズ
        serializer = CommentSerializer(comment)

        return serializer.data