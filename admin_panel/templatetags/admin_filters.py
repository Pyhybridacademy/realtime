from django import template

register = template.Library()

@register.filter
def replace(value, arg):
    """Replace all occurrences of a substring in a string."""
    old, new = arg.split(',', 1)  # Split arg into old and new substrings
    return value.replace(old, new)