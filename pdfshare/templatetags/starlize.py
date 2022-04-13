from django import template
import math
register = template.Library()

@register.filter()
def starlize(value):
    lista = []
    for v in range(math.floor(value/2)):
        lista.append(0)
    if value % 2 != 0:
        lista.append(1)
    while len(lista) < 5:
        lista.append(2)
    return lista