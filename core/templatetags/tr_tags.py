from django import template
register = template.Library()

@register.simple_tag
def t(obj, field):
    return obj.t(field)
