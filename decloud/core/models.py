import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _

from core import manager

__all__ = []


class User(AbstractUser):
    id = models.UUIDField(
        primary_key=True,
        unique=True,
        default=uuid.uuid4,
        editable=False,
    )
    username = None
    email = models.EmailField(
        "адрес электронной почты",
        unique=True,
    )

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = manager.UserManager()

    class Meta:
        """Meta class"""

        verbose_name = _("user")
        verbose_name_plural = _("users")
        indexes = [
            models.Index(fields=["id"]),
        ]

    def __str__(self):
        return self.email
