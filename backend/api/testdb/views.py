from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response

from .models import Hello

# Create your views here.
class Db(APIView):
    def get(self, request, format=None):
        # .first()を使えば、データがなくてもエラーにならない (Noneが返る)
        hello_object = Hello.objects.first()

        if hello_object:
            # データがあれば、そのテキストを返す
            return Response(hello_object.text)
        else:
            # データがなければ、親切なメッセージを返す
            return Response("データベースにデータがありません。", status=404)