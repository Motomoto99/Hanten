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
import openai
from django.conf import settings
from django.db.models import Subquery, OuterRef, Max
from django.db.models import Subquery, OuterRef, Max, Case, When, Exists,F
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
        
        # ベース。ここから “追記” で annotate していく（再代入で Room.objects... に戻さない）
        queryset = (
            Room.objects
            .select_related('theme')
            .annotate(participant_count=Count('participate', distinct=True))
            .order_by('-room_start')
        )

        # デフォルト（未ログイン/未登録時）
        queryset = queryset.annotate(
            is_participating=Value(False, output_field=BooleanField()),
            has_unread_messages=Value(False, output_field=BooleanField()),
        )

        if clerk_user_info and clerk_user_info.get('id'):
            try:
                user = User.objects.get(clerk_user_id=clerk_user_info['id'])

                # 参加中フラグ
                is_participating_subquery = Participate.objects.filter(
                    room=OuterRef('pk'), user=user
                )
                queryset = queryset.annotate(
                    is_participating=Exists(is_participating_subquery)
                )

                # 既読コメントの日時（CommentReadStatus → last_read_comment → post_date）
                last_read_time_sq = CommentReadStatus.objects.filter(
                    room=OuterRef('pk'),
                    user=user,
                ).values('last_read_comment__post_date')[:1]

                # 部屋ごとの最新コメント日時
                # ↓ ここは Comment の reverse name に合わせて修正してください。
                #   - related_name='comments' なら 'comments__post_date'
                #   - related_name 未指定(デフォルト)なら 'comment_set__post_date'
                queryset = queryset.annotate(
                    latest_comment_time=Max('comments__post_date'),   # ←要調整
                    last_read_time=Subquery(last_read_time_sq),
                ).annotate(
                    has_unread_messages=Case(
                        # 仕様：last_read が無い（まだ入室していない）なら False
                        When(last_read_time__isnull=True, then=Value(False)),
                        # 最新 > 既読 なら True
                        When(latest_comment_time__gt=F('last_read_time'), then=Value(True)),
                        default=Value(False),
                        output_field=BooleanField(),
                    )
                )

            except User.DoesNotExist:
                # 何もしない（デフォルトの False 注入が効いている）
                pass

        # 開催中/終了でフィルタ
        status = self.request.query_params.get('status', 'ongoing')
        now = timezone.now()
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

                # 既読状態を更新（最新のコメントを既読にする）
                CommentReadStatus.objects.update_or_create(
                    user=user,
                    room=room,
                    defaults={'last_read_comment': comment}
                )
                print("[SUCCESS] 既読状態を更新。")

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

client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
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
                defaults={'summary_text': self._generate_summary(room)}
            )

            # --- 個人へのフィードバックを生成 ---
            feedback_text = self._generate_private_feedback(summary, user, room)
            
            # --- DBに保存して、フロントに返す ---
            AIFeedbackPrivate.objects.create(room=room, user=user, feedback_text=feedback_text)
            
            return Response({"feedback": feedback_text}, status=status.HTTP_201_CREATED)

        except (User.DoesNotExist, Room.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

    def _generate_summary(self, room):
        print("★★★ AI: 要約を生成中... ★★★")
        # ★★★ 1. まず、この部屋の「参加者名簿」を、すべて取得します ★★★
        participants = Participate.objects.filter(room=room).select_related('user')
        # ★★★ 2. 誰がどの立場か、一瞬で分かる「早見表」を作っておきます ★★★
        positions_map = {p.user.id: p.get_position_display() for p in participants}

        # 3. 部屋のすべてのコメントを取得
        comments = Comment.objects.filter(room=room).select_related('user').order_by('post_date')

        # 4. 早見表を見ながら、議論のテキストを組み立てる
        discussion_text = "\n".join([
            f"- {c.user.user_name} ({positions_map.get(c.user.id, '立場不明')}派): {c.comment_text}" 
            for c in comments
        ])
        
        # 2. AIへの「お願い文（プロンプト）」を作成
        prompt = f"""
        以下のディベートの議論内容を300字程度で要約してください。議論の流れが分かるように、できるだけ具体的に書いてください。

        # 議論のテーマ
        {room.theme.theme_title}

        # 議論の内容
        {discussion_text}
        """

        try:
            print("★★★ AI: OpenAI APIに要約を依頼中... ★★★")
            # 3. OpenAI APIに、要約を依頼する
            response = client.chat.completions.create(
                model="gpt-3.5-turbo", # または "gpt-4" など
                messages=[
                    {"role": "system", "content": "あなたは優秀な議事録作成アシスタントです。"},
                    {"role": "user", "content": prompt}
                ]
            )
            print("★★★ AI: 要約の生成完了 ★★★")
            summary = response.choices[0].message.content
            return summary
        except Exception as e:
            print(f"OpenAI API (要約)エラー: {e}")
            return "AIによる要約の生成に失敗しました。"


    def _generate_private_feedback(self, summary, user, room):
        print(f"★★★ AI: {user.user_name}さんへのフィードバックを生成中... ★★★")
        # 1. このユーザーのコメントと、参加立場を取得
        user_comments = Comment.objects.filter(room=room, user=user).order_by('post_date')
        user_discussion_text = "\n".join([f"- {c.comment_text}" for c in user_comments])
        user_position = Participate.objects.get(room=room, user=user).get_position_display()

        # 2. AIへの、個人向けの「お願い文（プロンプト）」を作成
        prompt = f"""
        あなたは、ロジカルシンキングを教える、優れたディベートコーチです。
        以下の情報を基に、このユーザーの議論の進め方について、具体的で、役に立つ、優しいフィードバックを200字程度で作成してください。
        なお、相手の人格や価値観そのものを否定したり馬鹿にした入りするような発言がないかチェックし、あれば、自分と違う視点を理解し、自分の考えを深めることを促してください。

        # 議論全体の要約
        {summary.summary_text}

        # このユーザーが参加した立場
        {user_position}派

        # このユーザーが投稿した、すべてのコメント
        {user_discussion_text}
        """

        try:
            print("★★★ AI: OpenAI APIにフィードバックを依頼中... ★★★")
            # 3. OpenAI APIに、フィードバックを依頼する
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "あなたは優秀なディベートコーチです。"},
                    {"role": "user", "content": prompt}
                ]
            )
            print("★★★ AI: フィードバックの生成完了 ★★★")
            feedback = response.choices[0].message.content
            return feedback
        except Exception as e:
            print(f"OpenAI API (フィードバック)エラー: {e}")
            return "AIによるフィードバックの生成に失敗しました。"