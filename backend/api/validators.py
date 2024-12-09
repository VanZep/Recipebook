from rest_framework.serializers import ValidationError

from core.constants import MIN_VALUE, MAX_VALUE


def is_not_exists_objects_validator(obj, message):
    """Валидатор проверки, что объекты не существуют."""
    if not obj.exists():
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


def min_max_value_validator(value, part_of_message):
    """Валидатор проверки, минимального и максимального значений."""
    if value < MIN_VALUE or value > MAX_VALUE:
        raise ValidationError(
            f'{part_of_message} должно быть в диапазоне '
            f'от {MIN_VALUE} до {MAX_VALUE}.'
        )
