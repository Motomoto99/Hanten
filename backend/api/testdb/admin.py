from django.contrib import admin
from .models import Hello  # 自分のモデルをインポート

# Register your models here.
admin.site.register(Hello) # この一行を追加！