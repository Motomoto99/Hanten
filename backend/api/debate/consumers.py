# backend/api/debate/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from clerk_django.client import ClerkClient
import os
from channels.generic.websocket import WebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # グループに参加
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()
        print(f"WebSocket接続が確立されました。ルームID: {self.room_id}, グループ名: {self.room_group_name}")

    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f"WebSocket接続が切断されました。ルームID: {self.room_id}, グループ名: {self.room_group_name}")

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
            
        message_content = data.get('message')
        clerk_user_id = data.get('clerk_user_id')

        # ★★★ 必要な情報が含まれていなければ、何もしない ★★★
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
        print(f"メッセージを受信しました: {message_content}, 送信者ID: {clerk_user_id}")



    # グループからメッセージを受信してWebSocketに送信
    async def chat_message(self, event):
        await self.send(text_data=json.dumps(event))
        print(f"メッセージを送信しました: {event['message']}")

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

#動作確認用
class EchoConsumer(WebsocketConsumer):
    def connect(self):
        # 接続が来たら、無条件で受け入れる！
        self.accept()
        print("--- [ECHO] オウム返しサーバー：接続を受け入れました ---")

    def disconnect(self, close_code):
        print("--- [ECHO] オウム返しサーバー：切断されました ---")

    def receive(self, text_data):
        # メッセージを受け取ったら、そのまま送り返す！
        print(f"--- [ECHO] オウム返しサーバー：メッセージ '{text_data}' を受信。そのまま返します ---")
        self.send(text_data=f"オウム返し: {text_data}")