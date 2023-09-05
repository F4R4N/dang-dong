from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.utils import timezone
from rest_framework import status

from config.settings import (APP_NAME, AUTH_CODE_EXPIRES_IN, EMAIL_HOST_USER,
                             EMAIL_HTML_TEMPLATE_NAME,
                             EMAIL_PLAINTEXT_TEMPLATE_NAME, VERIFICATION_PATH)

from .models import Verification


def auth_email(user):
    plaintext = get_template(EMAIL_PLAINTEXT_TEMPLATE_NAME)
    html = get_template(EMAIL_HTML_TEMPLATE_NAME)
    subject = f"Verify its you in '{APP_NAME}'"
    if Verification.objects.filter(user=user, expire_at__gt=timezone.now()).exists():
        return status.HTTP_408_REQUEST_TIMEOUT, {
            "detail": "you asked for a magic_link recently wait after you can get new one"
        }

    code = Verification.objects.create(user=user).code
    context = {
        "username": user.email,
        "url": VERIFICATION_PATH + code,
        "expire_in_minutes": AUTH_CODE_EXPIRES_IN.total_seconds() / 60,
    }

    text_context = plaintext.render(context)
    html_context = html.render(context)
    msg = EmailMultiAlternatives(
        subject=subject, body=text_context, from_email=EMAIL_HOST_USER, to=[user.email]
    )
    msg.attach_alternative(html_context, "text/html")
    msg.send(fail_silently=False)
    return status.HTTP_200_OK, {"detail": "magic link has been sent to your email"}
