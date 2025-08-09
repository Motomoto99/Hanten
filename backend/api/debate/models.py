from django.db import models
from api.user.models import User  # usersアプリのモデルをインポート
from django.utils import timezone # timezoneをインポート

# Create your models here.
# テーマ (お題)
class Theme(models.Model):
    theme_title = models.CharField("テーマ文", max_length=255)
    theme_detail = models.TextField("テーマ詳細")

    def __str__(self):
        return self.theme_title

    class Meta:
        db_table = "theme"
    
# ディベート部屋
class Room(models.Model):
    room_name = models.CharField("ディベート部屋名", max_length=100)
    room_start = models.DateTimeField("ディベート開始日時", auto_now_add=True)
    room_end = models.DateTimeField("ディベート終了日時")
    theme = models.ForeignKey(Theme, on_delete=models.CASCADE, related_name="rooms", verbose_name="テーマ")
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name="created_rooms", verbose_name="作成者")

    def __str__(self):
        return self.room_name

    class Meta:
        db_table = "room"

# 参加者の立場（賛成か反対か）を表すモデル
class Participate(models.Model):
    # 参加立場（賛成か反対か）の選択肢
    class Position(models.TextChoices):
        AGREE = 'AGREE', '賛成'
        DISAGREE = 'DISAGREE', '反対'

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    position = models.CharField("立場", max_length=10, choices=Position.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "participate"
        # 同じユーザーが同じ部屋に複数参加できないように制約を設ける
        unique_together = ('user', 'room')