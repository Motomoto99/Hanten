# backend/api/debate/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # ▼▼▼【ここからが、新しい身元確認のロジックです！】▼▼▼
        try:
            # URLに添付された「チケット（トークン）」を取り出す
            query_string = self.scope['query_string'].decode()
            token = [p.split('=')[1] for p in query_string.split('&') if p.startswith('token=')][0]
            
            # Clerkに「このチケットは本物か？」と問い合わせる
            clerk_service = ClerkService()
            user_info = clerk_service.users.verify_token(token)
            
            # ★★★ 身元が確認できたので、ユーザー情報をscopeに保存する ★★★
            self.scope['clerk_user'] = user_info
            print(f"[SUCCESS] WebSocket 認証成功: user_id={user_info.get('id')}")

        except Exception as e:
            # チケットがない、偽物、期限切れなど、何か問題があれば接続を拒否
            print(f"[ERROR] WebSocket 認証失敗: {e}")
            await self.close()
            return

        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        await self.channel_layer.group_add(...)
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