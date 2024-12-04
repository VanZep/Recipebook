from rest_framework.permissions import IsAuthenticatedOrReadOnly, SAFE_METHODS


class IsAuthenticatedOrIsAuthorOrReadOnly(IsAuthenticatedOrReadOnly):
    """Разрешение для аутентифицированного пользователя,
    автора контента или только чтение для анонимного пользователя.
    """

    def has_object_permission(self, request, view, obj):
        return request.method in SAFE_METHODS or request.user == obj.author
