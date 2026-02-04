from django import template
from django.utils.safestring import mark_safe
import re

register = template.Library()

@register.filter
def bold_labels(text: str):
    if not text:
        return ""

    # Pogrub "Skład:" / "Składniki"
    out = re.sub(
        r'(^|\n)\s*(Składniki?|Skład)\s*:',
        r'\1<strong>\2:</strong>',
        text,
        flags=re.IGNORECASE
    )

    # zachowaj nowe linie (żeby nie zlało się w jeden akapit)
    out = out.replace("\n", "<br>")
    return mark_safe(out)
