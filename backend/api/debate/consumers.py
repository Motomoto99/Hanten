# backend/api/debate/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
# from .models import Room, Message, User

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

    async def disconnect(self, close_code):
        # グループから離脱
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # WebSocketでメッセージを受信
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_content = data['message']
        clerk_user_id = data['clerk_user_id']
        
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
        message = event['message']
        await self.send(text_data=json.dumps(message))

    @database_sync_to_async
    def save_message(self, content, clerk_user_id):
        sender = User.objects.get(clerk_user_id=clerk_user_id)
        room = Room.objects.get(id=self.room_id)
        message = Message.objects.create(room=room, sender=sender, content=content)
        # 本来はシリアライザーを使うべきですが、簡潔にするため辞書を作成
        return {
            'id': message.id,
            'sender': { 'user_name': sender.user_name },
            'content': message.content,
            'created_at': message.created_at.isoformat()
        }