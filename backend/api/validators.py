from rest_framework.serializers import ValidationError


def is_exists_objects_validator(obj, message):
    """Валидатор проверки, что объекты существуют."""
    if obj.exists():
        raise ValidationError({'detail': message})


def is_not_exists_objects_validator(obj, message):
    """Валидатор проверки, что объекты не существуют."""
    if not obj.exists():
        raise ValidationError({'detail': message})


def user_is_author_validator(user, author, message):
    """Валидатор проверки, что пользователь есть автор объекта."""
    if user == author:
        raise ValidationError({'detail': message})
