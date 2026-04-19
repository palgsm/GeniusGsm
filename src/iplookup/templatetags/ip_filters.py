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


@register.filter(name='get_item')
def get_item(dictionary, key):
    """Get an item from a dictionary using a key."""
    try:
        return dictionary.get(key) if isinstance(dictionary, dict) else dictionary[key]
    except (KeyError, TypeError, AttributeError):
        return None

