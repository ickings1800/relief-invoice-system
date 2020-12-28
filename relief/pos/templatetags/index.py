from django import template
from datetime import datetime

register = template.Library()

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def keyvalue(dict, key):
    return dict[key]

@register.filter
def keyvalueget(dict, key):
    return dict.get(key)

@register.filter
def all_quantity_zero(List):
    for item in List:
        if item.quantity > 0:
            return False
    return True

@register.filter
def format_date(date, fmt):
	return date.strftime(fmt)
