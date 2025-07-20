from .base import *

DEBUG = False

# Renderのホスト名を許可
RENDER_EXTERNAL_HOSTNAME = os.environ.get('RENDER_EXTERNAL_HOSTNAME')
if RENDER_EXTERNAL_HOSTNAME:
    ALLOWED_HOSTS.append(RENDER_EXTERNAL_HOSTNAME)


# ======== データベース設定（最重要！）========

# 環境変数 DATABASE_URL を取得
DATABASE_URL = os.environ.get('DATABASE_URL')

# もしDATABASE_URLが設定されていなかったら、分かりやすいエラーを出す
if DATABASE_URL is None:
    raise ImproperlyConfigured("本番環境変数 'DATABASE_URL' が設定されていません。Renderのダッシュボードを確認してください。")

# dj-database-url を使って設定を読み込む (SSL接続を必須にする)
DATABASES = {
    'default': dj_database_url.config(conn_max_age=600, ssl_require=True)
}



CORS_ALLOWED_ORIGINS = [
    "https://hanten-psi.vercel.app",   # ← 本番用の、Vercelの住所をここに追加！(あなたのURLに変えてくださいね)
]