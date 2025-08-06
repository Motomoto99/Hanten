from rest_framework.permissions import BasePermission

class ClerkAuthenticated(BasePermission):
    """
    Clerkによって認証されたユーザーのみにアクセスを許可する、
    私たち専用のカスタムパーミッションです。
    """
    message = "認証されていません。有効なClerkのトークンを提供してください。"

    def has_permission(self, request, view):
        # Clerkのミドルウェアが追加してくれた`request.auth`が存在し、
        # かつ、中身が空っぽ(None)でなければ、アクセスを許可します。
        return hasattr(request, 'auth') and request.auth is not None