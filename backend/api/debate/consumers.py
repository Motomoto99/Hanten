# backend/api/debate/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from clerk_django.client import ClerkClient
import os

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # asgi.pyのClerkAsyncAuthMiddlewareが、すでに認証を済ませてくれている
        # 私たちは、その結果（身分証明書）を、ただ信じるだけ
        if not hasattr(self.scope, 'clerk_user') or not self.scope['clerk_user']:
            print("[ERROR] WebSocket 認証失敗: 身分証明書が見つかりません。")
            await self.close()
            return

        user_info = self.scope['clerk_user']
        print(f"[SUCCESS] WebSocket 認証成功: user_id={user_info.get('sub')}")

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