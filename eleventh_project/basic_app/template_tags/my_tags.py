from django import template

register = template.Library()

@register.filter('cut')
def cut(value, arg):
    return value.replace(arg, '')
