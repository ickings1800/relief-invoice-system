from django import template
register = template.Library()

@register.filter
def index(List, i):
    return List[int(i)]

@register.filter
def keyvalue(dict, key):
    return dict.get(key)
