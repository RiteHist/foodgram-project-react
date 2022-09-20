from django.core.validators import RegexValidator


class SlugValidator(RegexValidator):
    regex = '^[-a-zA-Z0-9_]+$'


def min_amount(amount):
    if amount <= 0:
        raise ValueError('Количество не может быть меньше 1.')
