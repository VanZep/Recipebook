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


def is_not_selected_validator(obj, name):
    """Валидатор проверки, что объект не выбран."""
    if not obj:
        raise ValidationError(
            f'Нужно выбрать хотя бы один {name}'
        )


def only_one_selected_validator(obj_list, name):
    """Валидатор проверки, что объект уже выбран."""
    if len(obj_list) != len(set(obj_list)):
        raise ValidationError(
            f'Каждый {name} можно выбрать только один раз'
        )
