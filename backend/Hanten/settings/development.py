from .base import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('POSTGRES_DB'),
        'USER': os.environ.get('POSTGRES_USER'),
        'PASSWORD': os.environ.get('POSTGRES_PASSWORD'),
        'HOST': 'db',  # docker-compose.ymlで定義したサービス名
        'PORT': '5432',
    }
}



STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'


CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000", # フロントエンド（Next.js）からのアクセスを許可
    "http://127.0.0.1:3000",  # 念のため、こちらも追加
]

# =================================================================
#  管理者ユーザー自動作成用の設定
# =================================================================
# 環境変数からスーパーユーザーの情報を読み込んで、settingsの一部として定義する
SUPERUSER_NAME = os.environ.get('SUPERUSER_NAME')
SUPERUSER_EMAIL = os.environ.get('SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = os.environ.get('SUPERUSER_PASSWORD')