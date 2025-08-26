from django.shortcuts import render

from rest_framework.views import APIView
from rest_framework import generics, status
from .serializers import RoomListSerializer, RoomDetailSerializer,RoomCreateSerializer,CommentSerializer, ThemeSerializer
from django.db.models import Count # Countをインポート
from api.pagination import StandardResultsSetPagination # 作成したページネーションをインポート
from rest_framework.response import Response
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from .models import Room, Theme, User,Participate,Comment, CommentReadStatus, AIFeedbackPrivate, AIFeedbackSummary
from django.db.models import Exists, OuterRef, Count, Value,BooleanField
from django.http import JsonResponse
# from api.permissions.clerk import ClerkAuthenticated

# ディベート部屋の一覧を取得・作成するAPIビュー
class DebateListCreateAPIView(generics.ListCreateAPIView):
    serializer_class = RoomListSerializer
    # permission_classes = [ClerkAuthenticated]

    def get_queryset(self):
        """
        URLのクエリパラメータに応じて、開催中か終了済みかをフィルタリングする
        """
        # まず、Clerkの認証情報を安全に取得
        clerk_user_info = getattr(self.request, 'clerk_user', None)
        
        # 基本となるクエリセットを用意
        queryset = Room.objects.select_related('theme').annotate(
            participant_count=Count('participate', distinct=True)
        ).order_by('-room_start')

        # Clerkの認証情報が存在し、IDが取得できる場合のみ、参加状態をチェックする
        if clerk_user_info and clerk_user_info.get('id'):
            try:
                # 本物の身分証明書(clerk_user_id)を使って、DBから本当のユーザーを探す
                user = User.objects.get(clerk_user_id=clerk_user_info.get('id'))
                
                # 見つけた本当のユーザーで、参加状態を問い合わせるサブクエリを作成
                is_participating_subquery = Participate.objects.filter(
                    room=OuterRef('pk'), 
                    user=user
                )
                queryset = queryset.annotate(is_participating=Exists(is_participating_subquery))

            except User.DoesNotExist:
                # 万が一、ClerkにはいるがDBにいないユーザーの場合（ありえないはずですが念のため）
                queryset = queryset.annotate(is_participating=Value(False, output_field=BooleanField()))
        else:
            # ログインしていない、または認証情報が不正なユーザーは、何にも参加していない
            queryset = queryset.annotate(is_participating=Value(False, output_field=BooleanField()))

        # ... (以降のフィルタリングロジックは変更なし)
        status = self.request.query_params.get('status', 'ongoing')
        now = timezone.now()
        print(f"--- [DEBUG] サーバーの現在時刻 (UTC): {now} ---")

        if status == 'ongoing':
            return queryset.filter(room_end__gt=now)
        elif status == 'finished':
            return queryset.filter(room_end__lte=now)
        
        return queryset

    def get_serializer_class(self):
        """
        リクエストのメソッドに応じて、使用するシリアライザーを切り替える
        """
        if self.request.method == 'POST':
            return RoomCreateSerializer
        return RoomListSerializer

    def perform_create(self, serializer):
        """
        POSTリクエストで部屋を作成する際の追加ロジック
        """
        serializer.save()

# 参加者数をカウントして、レスポンスに含める
class ThemeListAPIView(generics.ListAPIView):
    queryset = Theme.objects.all()
    serializer_class = ThemeSerializer

class DebateDetailAPIView(generics.RetrieveAPIView):
    """
    個別のディベート部屋の詳細を取得するAPI
    """
    queryset = Room.objects.select_related('theme', 'creator')
    serializer_class = RoomDetailSerializer
    # permission_classes = [ClerkAuthenticated]

# ディベート部屋に最初のメッセージを投稿するAPI
class FirstMessageAPIView(generics.CreateAPIView):

    def create(self, request, *args, **kwargs):
        room_id = self.kwargs.get('pk')
        content = request.data.get('content')
        position = request.data.get('position') # 'AGREE' or 'DISAGREE'

        if not all([content, position]):
            return Response({"error": "必須項目が不足しています"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # ==================== 監視カメラ 2: 身元確認 ====================
            clerk_user_id = request.clerk_user.get('id')
            print(f"[DEBUG] ユーザーを検索します... Clerk ID: {clerk_user_id}")
            user = User.objects.get(clerk_user_id=clerk_user_id)
            print(f"[SUCCESS] ユーザーを発見: {user.email}")

            # ==================== 監視カメラ 3: 部屋の確認 ====================
            print(f"[DEBUG] ディベート部屋を検索します... Room ID: {room_id}")
            room = Room.objects.get(id=room_id)
            print(f"[SUCCESS] 部屋を発見: {room.room_name}")

            # ==================== 監視カメラ 4: トランザクション開始 ====================
            print("[INFO] データベースへの書き込み処理を開始します...")
            with transaction.atomic():
                actual_position= 'DISAGREE' if position.upper() == 'AGREE' else 'AGREE'
                # 参加者として登録（既に参加済みの場合は何もしない）
                participation, created = Participate.objects.get_or_create(
                    user=user,
                    room=room,
                    defaults={'position': actual_position.upper()}
                )
                if created:
                    print(f"[SUCCESS] 参加者として新規登録完了。")
                else:
                    print(f"[INFO] 既に参加済みのため、参加登録はスキップ。")

                # 最初のメッセージを投稿
                comment = Comment.objects.create(
                    room=room,
                    user=user,
                    comment_text=content
                )
                print("[SUCCESS] 最初のメッセージの投稿完了。")
                # ★★★ WebSocketグループにメッセージをブロードキャスト ★★★
                channel_layer = get_channel_layer()
                async_to_sync(channel_layer.group_send)(
                    f'chat_{room.id}',
                    {
                        'type': 'chat_message',
                        'message': CommentSerializer(comment).data
                    }
                )
            
            print("--- [COMPLETE] すべての処理が成功しました ---")
            return Response({"message": "投稿に成功しました"}, status=status.HTTP_201_CREATED)
        except User.DoesNotExist:
            print(f"[FATAL] ユーザーが見つかりません。Clerk ID: {clerk_user_id}")
            return Response({"error": "認証されたユーザーがデータベースに存在しません。"}, status=status.HTTP_404_NOT_FOUND)
        except Room.DoesNotExist:
            print(f"[FATAL] ディベート部屋が見つかりません。Room ID: {room_id}")
            return Response({"error": "指定されたディベート部屋が存在しません。"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            # その他の予期せぬエラー（DBの制約違反など）
            print(f"[FATAL] 予期せぬサーバーエラーが発生しました: {str(e)}")
            return Response({"error": f"サーバー内部でエラーが発生しました: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ディベート部屋のメッセージ一覧を取得するAPI
class MessageListAPIView(generics.ListAPIView):
    """
    指定されたディベート部屋のメッセージ一覧を、ページネーションして返す、ただそれだけのAPI
    """
    serializer_class = CommentSerializer
    # pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        room_id = self.kwargs.get('pk')
        # CommentモデルのForeignKeyは 'user' なので、'user' をselect_relatedします
        return Comment.objects.filter(room_id=room_id).select_related('user')

    def list(self, request, *args, **kwargs):
        # まず、すべてのメッセージを取得します
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        
        # 次に、このユーザーの「栞」を探します
        last_read_status = None
        if hasattr(request, 'clerk_user') and request.clerk_user.get('id'):
            try:
                user = User.objects.get(clerk_user_id=request.clerk_user.get('id'))
                last_read_status = CommentReadStatus.objects.filter(
                    room_id=self.kwargs.get('pk'),
                    user=user
                ).first()
            except User.DoesNotExist:
                pass

        # 最後に、メッセージリストと「栞」を、一つの綺麗な箱に入れて返します
        response_data = {
            'results': serializer.data,
            'last_read_comment_id': last_read_status.last_read_comment_id if last_read_status else None
        }
        return Response(response_data)


# ★★★ 既読状態を更新するためのAPIビュー ★★★ まだできてない
class ReadStatusUpdateAPIView(APIView):
    serializer_class = CommentSerializer
    pagination_class = StandardResultsSetPagination # 既存のページネーションを再利用

    def post(self, request, pk):
        last_read_comment_id = request.data.get('last_read_comment_id')
        if not last_read_comment_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(clerk_user_id=request.clerk_user.get('id'))
            
            # ★★★ ここも「user」に統一！ ★★★
            CommentReadStatus.objects.update_or_create(
                user=user,
                room_id=pk,
                defaults={'last_read_comment_id': last_read_comment_id}
            )
            return Response(status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

# ★★★ AIフィードバックを生成・取得するためのAPI ★★★
class AIFeedbackView(APIView):

    def get(self, request, pk):
        try:
            user = User.objects.get(clerk_user_id=request.clerk_user.get('id'))
            feedback = AIFeedbackPrivate.objects.get(room_id=pk, user=user)
            return Response({"feedback": feedback.feedback_text})
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)
        except AIFeedbackPrivate.DoesNotExist:
            # フィードバックがまだ存在しない場合は、空のレスポンスを返す
            return Response({"feedback": None})


    def post(self, request, pk):
        try:
            user = User.objects.get(clerk_user_id=request.clerk_user.get('id'))
            room = Room.objects.get(id=pk)

            # --- このユーザーへのフィードバックが既に存在するか確認 ---
            existing_feedback = AIFeedbackPrivate.objects.filter(room=room, user=user).first()
            if existing_feedback:
                return Response({"feedback": existing_feedback.feedback_text})

            # --- 議論全体の要約が存在するか確認、なければ生成 ---
            summary, created = AIFeedbackSummary.objects.get_or_create(
                room=room,
                defaults={'summary_text': self.generate_summary(room)}
            )

            # --- 個人へのフィードバックを生成 ---
            feedback_text = self.generate_private_feedback(summary, user, room)
            
            # --- DBに保存して、フロントに返す ---
            AIFeedbackPrivate.objects.create(room=room, user=user, feedback_text=feedback_text)
            
            return Response({"feedback": feedback_text}, status=status.HTTP_201_CREATED)

        except (User.DoesNotExist, Room.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def generate_summary(self, room):
        # ★★★ ここに、OpenAI APIを呼び出すロジックを実装します ★★★
        # all_comments = Comment.objects.filter(room=room)
        # prompt = "以下のコメントを要約してください..."
        print("★★★ AI: 要約を生成中... ★★★")
        return "これは、AIによって生成された、ディベート全体の要約です。"

    def generate_private_feedback(self, summary, user, room):
        # ★★★ ここに、OpenAI APIを呼び出すロジックを実装します ★★★
        # user_comments = Comment.objects.filter(room=room, user=user)
        # prompt = f"要約は「{summary.summary_text}」です。このユーザーのコメントを基に..."
        print(f"★★★ AI: {user.user_name}さんへのフィードバックを生成中... ★★★")
        return "これは、AIによって生成された、あなただけのプライベートなフィードバックです。"