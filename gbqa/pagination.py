import math
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response


class CustomPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = 'per_page'
    max_page_size = 100

    def get_paginated_response(self, data):
        return Response({
            'pagination': {
                'links': {
                    'next': self.get_next_link(),
                    'previous': self.get_previous_link()
                },
                'current_page': self.page.number,
                'total': self.page.paginator.count,
                'per_page':
                    self.page_size
                    if self.request.query_params.get(self.page_size_query_param, None) is None
                    else int(self.request.query_params.get(self.page_size_query_param)),
                'last_page': math.ceil(self.page.paginator.count / self.page_size)
            },
            'results': data
        })
