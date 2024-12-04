from rest_framework.pagination import PageNumberPagination

from core.constants import PAGE_SIZE


class PageNumberLimitPagination(PageNumberPagination):
    """Класс пагинации."""

    page_size = PAGE_SIZE
    page_size_query_param = 'limit'
