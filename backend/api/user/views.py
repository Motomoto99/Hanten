from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status
from rest_framework import generics

from api.user.models import User
from api.debate.models import Room, Participate, Comment
from .serializers import UserSerializer
from api.debate.serializers import RoomListSerializer
from .serializers import DebateEvaluationSerializer,UserProfileSerializer
from django.db.models import Count
from django.db.models import Exists, OuterRef, Count, Value,BooleanField
from django.utils import timezone


class Me(APIView):
    """
    ログイン中のユーザー情報を取得する
    """
    def get(self, request): #GETリクエストの場合かな
        print("--- /api/user/me/ GETリクエスト受信 ---")
        # Clerkが認証したユーザーIDを取得
        clerk_user_id = request.clerk_user.get('id')
        if not clerk_user_id:
            print("[ERROR] 環境変数 'CLERK_SECRET_KEY' が設定されていません！")
            return Response({"error": "認証されていません"}, status=401)

        #ClerkのWebhookはより先にこっちでユーザーを探しても見つからないからここで検索して見つからなかったら登録する
        # try:
        #     # まず、メールアドレスで既存ユーザーを探す
        #     user = User.objects.get(email=email_address)
                
        #     # 見つかった -> 復帰処理
        #     user.clerk_user_id = clerk_user_id # 新しいClerk IDに更新
        #     user.deleted_date = None          # 退会日を消去
        #     user.first_flag = True            # もう一度初回ログイン扱いに
        #     user.save()

        # except User.DoesNotExist:
        #     # 見つからなかった -> 本当の新規登録
        #     User.objects.create(
        #         clerk_user_id=clerk_user_id,
        #         email=email_address,
        #         user_name=clerk_user_id # 仮のユーザー名
        #     )

        try:
            print("IDを基にユーザー情報を取得開始...",clerk_user_id)
            # Clerk IDを元に、データベースから自分のユーザー情報を探す
            user = User.objects.get(clerk_user_id=clerk_user_id)
            serializer = UserSerializer(user)
            # フロントエンドに、綺麗なJSONで情報を返す
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが見つかりません"}, status=404)

    """
    初回ログイン時のプロフィール情報を更新する
    """
    def put(self, request):
        clerk_user_id = request.clerk_user.get('id')
        if not clerk_user_id:
            return Response({"error": "認証されていません"}, status=status.HTTP_401_UNAUTHORIZED)

        # Clerk IDを元に、更新対象のユーザーを取得
        try:
            print("IDを基にユーザー情報を取得開始...", clerk_user_id)
            user = User.objects.get(clerk_user_id=clerk_user_id)
        except User.DoesNotExist:
            return Response({"error": "ユーザーが見つかりません"}, status=status.HTTP_404_NOT_FOUND)

        # フロントエンドから送られてきた新しいユーザー名を取得
        new_user_name = request.data.get('user_name')
        if not new_user_name:
            return Response({"error": "ユーザー名が指定されていません"}, status=status.HTTP_400_BAD_REQUEST)
        
        print('/user/me/のPUTリクエスト受信:', clerk_user_id, new_user_name)
        # ユーザー名と初回フラグを更新
        user.user_name = new_user_name
        user.first_flag = False
        user.save()

        return Response(status=status.HTTP_200_OK)

# ★★★ ユーザーが参加したディベート一覧を返すAPI ★★★
class ParticipatedDebateListView(generics.ListAPIView):
    serializer_class = RoomListSerializer

    def get_queryset(self):
        try:
            # まず、このリクエストを送ってきた「本当の」ユーザーを探し出す
            user = User.objects.get(clerk_user_id=self.request.clerk_user.get('id'))
        except User.DoesNotExist:
            # もしユーザーが見つからなければ、空っぽのリストを返す
            return Room.objects.none()
        
        # ★★★ 1. まず、すべての部屋の、本当の参加人数を数える ★★★
        all_rooms_with_count = Room.objects.select_related('theme').annotate(
            participant_count=Count('participate', distinct=True),
            is_participating=Value(True, output_field=BooleanField())
        )

        # ★★★ 2. その後で、このユーザーが参加している部屋だけを、選び出す ★★★
        queryset = all_rooms_with_count.filter(participants=user).order_by('-room_start')

        # ステータス（開催中か終了済みか）でフィルタリング
        status = self.request.query_params.get('status', 'ongoing')
        now = timezone.now()
        if status == 'ongoing':
            return queryset.filter(room_end__gt=now)
        elif status == 'finished':
            return queryset.filter(room_end__lte=now)
        return queryset

class DebateEvaluationView(APIView):

    def get(self, request, debateId):
        try:
            user = User.objects.get(clerk_user_id=request.clerk_user.get('id'))
            room = Room.objects.get(id=debateId)

            # --- 1. コメント関連の集計 ---
            all_comments_in_room = Comment.objects.filter(room=room)
            total_comment_count = all_comments_in_room.count()
            my_comment_count = all_comments_in_room.filter(user=user).count()
            
            my_comment_percentage = (my_comment_count / total_comment_count * 100) if total_comment_count > 0 else 0

            # --- 2. 立場の比率の集計 ---
            participants_in_room = Participate.objects.filter(room=room)
            total_participants = participants_in_room.count()
            agree_count = participants_in_room.filter(position='AGREE').count()
            
            agree_percentage = (agree_count / total_participants * 100) if total_participants > 0 else 0
            disagree_percentage = 100 - agree_percentage
            
            # --- 3. データをまとめる ---
            data = {
                'my_comment_count': my_comment_count,
                'my_comment_percentage': round(my_comment_percentage, 1),
                'total_comment_count': total_comment_count,
                'agree_percentage': round(agree_percentage, 1),
                'disagree_percentage': round(disagree_percentage, 1),
            }

            serializer = DebateEvaluationSerializer(data=data)
            serializer.is_valid(raise_exception=True)
            return Response(serializer.data)

        except (User.DoesNotExist, Room.DoesNotExist):
            return Response(status=status.HTTP_404_NOT_FOUND)

# ★★★ ユーザープロフィール情報を返す、一人目の秘書 ★★★
class UserProfileView(APIView):

    def get(self, request):
        try:
            user = User.objects.annotate(
                # Userモデルに、参加したディベートの数を一時的にくっつけます
                participated_count=Count('participating_rooms')
            ).get(clerk_user_id=request.clerk_user.get('id'))
            
            serializer = UserProfileSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND)

# ★★★ ユーザーが作成したディベート一覧を返す、二人目の秘書 ★★★
class CreatedDebateListView(generics.ListAPIView):
    serializer_class = RoomListSerializer

    def get_queryset(self):
        # このリクエストを送ってきたユーザーを探し出し…
        user = User.objects.get(clerk_user_id=self.request.clerk_user.get('id'))
        # その人が「作成者」になっている部屋だけを、絞り込んで返すのです
        return Room.objects.filter(creator=user).select_related('theme').annotate(
            participant_count=Count('participate', distinct=True),
            is_participating=Value(True, output_field=BooleanField()) # 自分が作った部屋は、当然「参加済み」ですわ
        ).order_by('-room_start')