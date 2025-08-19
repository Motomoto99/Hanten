# backend/api/debate/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from clerk_django.client import ClerkClient
import os

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            query_string = self.scope['query_string'].decode()
            token = [p.split('=')[1] for p in query_string.split('&') if p.startswith('token=')][0]
            
            # ▼▼▼【これが、最後の、そして最も確実な呪文です！】▼▼▼
            # 門番を呼び出す際に、直接、秘密の合言葉を渡す！
            clerk_client = ClerkClient(secret_key=os.environ.get("CLERK_SECRET_KEY"))
            
            payload = clerk_client.verify_token(token)
            
            self.scope['clerk_user'] = payload 
            print(f"[SUCCESS] WebSocket 認証成功: user_id={payload.get('sub')}")

        except Exception as e:
            print(f"[ERROR] WebSocket 認証失敗: {e}")
            await self.close()
            return

        # 部屋に参加する処理
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # WebSocketでメッセージを受信
    async def receive(self, text_data):
        try:
            # 接続時に保証された、安全な身分証明書からユーザーIDを取得
            clerk_user_id = self.scope['clerk_user'].get('sub')
            message_content = json.loads(text_data).get('message')

            if not all([message_content, clerk_user_id]):
                return
            
            new_message_data = await self.save_and_serialize_message(message_content, clerk_user_id)

            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': new_message_data
                }
            )
        except Exception as e:
            print(f"WebSocket receive error: {e}")
    
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