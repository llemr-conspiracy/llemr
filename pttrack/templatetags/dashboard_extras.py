from django import template

register = template.Library()

@register.filter
def as_percentage_of(part, whole):
    try:
    	print(whole)
        return "%d%%" % (float(part) / float(whole) * 100)
    except (ValueError, ZeroDivisionError):
        return ""