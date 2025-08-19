from rest_framework.permissions import BasePermission

class ClerkAuthenticated(BasePermission):
    """
    Clerkによって認証されたユーザーのみにアクセスを許可する、
    私たち専用のカスタムパーミッションです。
    """
    message = "認証されていません。有効なClerkのトークンを提供してください。"

    def has_permission(self, request, view):
        # ▼▼▼【ここを、'auth'から'clerk_user'に、正しく書き換えます！】▼▼▼
        # Clerkのミドルウェアが追加してくれた`request.clerk_user`が存在すれば、アクセスを許可します。
        return hasattr(request, 'clerk_user') and request.clerk_user is not None