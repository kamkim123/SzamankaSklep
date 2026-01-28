from urllib.parse import urlsplit, urlunsplit
from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def canonical_no_query(context):
    request = context["request"]
    parts = urlsplit(request.build_absolute_uri())
    return urlunsplit((parts.scheme, parts.netloc, parts.path, "", ""))
