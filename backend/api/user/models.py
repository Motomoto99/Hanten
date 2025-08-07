from django.db import models

# Create your models here.

class User(models.Model):
    # ClerkユーザーID (clerk_user_id)
    clerk_user_id = models.CharField(
        max_length=50, 
        unique=True, # 同じIDは登録できないようにする
        verbose_name="ClerkユーザーID" # 管理サイトで表示される名前
    )

    # ユーザー名 (user_name)
    user_name = models.CharField(
        max_length=50,
        unique=True, # ユーザー名は他の人と同じものは使えないようにする
        verbose_name="ユーザー名"
    )

     # ユーザーを特定するための、一番大事なキーになります
    email = models.EmailField(
        unique=True,
        verbose_name="メールアドレス"
    )

    # 初回ログインフラグ (first_flag)
    first_flag = models.BooleanField(
        default=True, # 新規ユーザーは必ず初回ログインなので、Trueをデフォルトにします
        verbose_name="初回ログインフラグ"
    )

    # 退会日時 (deleted_date)
    deleted_date = models.DateTimeField(
        null=True,     # データベース上でNULLを許可する
        blank=True,    # フォーム入力で空欄を許可する
        default=None,  # デフォルト値はNULL
        verbose_name="退会日時"
    )

    class Meta:
        db_table = "user"