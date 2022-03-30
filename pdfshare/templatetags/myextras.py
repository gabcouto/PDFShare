from django import template

register = template.Library()

@register.filter()
def myextras(min=5):
    return range(min)