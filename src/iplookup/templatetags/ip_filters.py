from django import template

register = template.Library()


@register.filter(name='length_is')
def length_is(value, arg):
    """Return True if len(value) == int(arg).

    Works with sequences and dicts; returns False for None or non-iterables.
    """
    try:
        expected = int(arg)
    except (TypeError, ValueError):
        return False

    try:
        return len(value) == expected
    except Exception:
        return False
