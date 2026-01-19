# orders/emails.py
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string


def send_order_email(order, *, subject: str, template_base: str, extra_ctx: dict | None = None) -> None:
    """
    template_base np. "orders/emails/order_created"
    -> użyje:
       - orders/emails/order_created.html
       - orders/emails/order_created.txt
    """
    ctx = {
        "order": order,
        "items": order.items.select_related("product").all(),
        "site_name": getattr(settings, "SITE_NAME", "SzamankaSklep"),
        "support_email": getattr(settings, "DEFAULT_FROM_EMAIL", ""),
        "company_name": getattr(settings, "COMPANY_NAME", ""),
        "company_iban": getattr(settings, "COMPANY_IBAN", ""),
    }
    if extra_ctx:
        ctx.update(extra_ctx)

    to_email = order.email
    if not to_email:
        return

    text_body = render_to_string(f"{template_base}.txt", ctx)
    html_body = render_to_string(f"{template_base}.html", ctx)

    msg = EmailMultiAlternatives(
        subject=subject,
        body=text_body,
        from_email=getattr(settings, "DEFAULT_FROM_EMAIL", None),
        to=[to_email],
    )
    msg.attach_alternative(html_body, "text/html")
    msg.send(fail_silently=False)
