import os
from typing import Optional

from django.core.mail import send_mail
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes
from django.conf import settings

from users.models import Profile


def send_sign_in_email(user: Profile) -> None:
    token = default_token_generator.make_token(user)
    uid = urlsafe_base64_encode(force_bytes(user.pk))
    verification_link = f"{os.environ['EMAIL_VERIFICATION_URL']}/{uid}/{token}/"

    subject = 'Verify your email address 🚀'
    message = (
        'Hi there 🙂\n'
        'Please click '
        f'<a href="{verification_link}" target="_blank">here</a> '
        'to verify your email address'
    )
    send_mail(subject, '', settings.EMAIL_HOST_USER, [user.email], html_message=message)


def decode_uid(uidb64: str) -> Optional[str]:
    """Decode the base64 encoded UID."""
    try:
        return urlsafe_base64_decode(uidb64).decode()
    except (TypeError, ValueError, OverflowError) as e:
        print(f'{e = }')
        return None


def get_user_by_uid(uid: str) -> Optional[Profile]:
    """Retrieve user object using UID."""
    try:
        return Profile.objects.get(pk=uid)
    except Profile.DoesNotExist as e:
        print(f'{e = }')
        return None