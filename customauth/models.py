import secrets

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models
from django.utils import timezone

from api.utils import generate_id
from config.settings import AUTH_CODE_EXPIRES_IN, LANGUAGES


class User(AbstractUser):
    id = models.SlugField(
        max_length=100, default=generate_id, unique=True, primary_key=True
    )
    email = models.EmailField(blank=False, null=False, unique=True)
    username = models.CharField(
        unique=True, max_length=250, validators=[UnicodeUsernameValidator()]
    )
    preferred_language = models.CharField(max_length=10, choices=LANGUAGES, default="en")


class Verification(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    code = models.CharField(max_length=100, unique=True)
    created_time = models.DateTimeField()
    expire_at = models.DateTimeField()

    def save(self, *args, **kwargs):
        self.created_time = timezone.now()
        self.expire_at = self.created_time + AUTH_CODE_EXPIRES_IN
        self.code = secrets.token_urlsafe(20)
        return super().save()

    def is_expired(self):
        if self.expire_at > timezone.now():
            return False
        return True
