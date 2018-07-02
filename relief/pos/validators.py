from django.core.exceptions import ValidationError
from datetime import datetime


def date_within_year(value):
    try:
        if not 1 >= (value.year - datetime.today().year) >= 0:
            raise ValidationError(
                'Date given is not greater or within current year.'
            )
    except ValueError as e:
        raise ValidationError('Invalid date given')
