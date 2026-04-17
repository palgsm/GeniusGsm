from django import template
from project.views import get_seo_config

register = template.Library()


@register.simple_tag
def seo_config(app_name):
    """
    Template tag to load SEO configuration for a specific app
    Usage in template: {% seo_config 'iplookup' as seo %}
    """
    return get_seo_config(app_name)


@register.filter
def get_keywords(app_name):
    """
    Template filter to get keywords for an app
    Usage: {{ 'iplookup'|get_keywords }}
    """
    config = get_seo_config(app_name)
    if config:
        return config['meta_keywords']
    return ""


@register.filter
def get_meta_description(app_name):
    """
    Template filter to get meta description for an app
    Usage: {{ 'iplookup'|get_meta_description }}
    """
    config = get_seo_config(app_name)
    if config:
        return config['meta_description']
    return ""
