from rest_framework.serializers import ValidationError


def is_exists_objects_validator(obj):
    """Валидатор существования объектов."""
    if not obj.exists():
        raise ValidationError({'detail': 'Объект не найден'})
