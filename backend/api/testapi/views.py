from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

# Create your views here.
class Backend(APIView):
    def get(self, request, format=None):
        return Response({"message": "backend"})

