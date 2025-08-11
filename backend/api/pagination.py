from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20  # 1ページあたりのデフォルトのアイテム数
    page_size_query_param = 'page_size' # URLで件数を指定できるようにする
    max_page_size = 100 # 1度にリクエストできる最大件数

    def get_paginated_response(self, data):
        return Response({
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'count': self.page.paginator.count,
            'results': data
        })