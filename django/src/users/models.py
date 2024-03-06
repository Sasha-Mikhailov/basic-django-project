from typing import ClassVar
import uuid

from django.contrib.auth.models import AbstractUser
from django.contrib.auth.models import UserManager as _UserManager
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):  # noqa
    class Role(models.TextChoices):
        ADMIN = "ADMIN", _("Admin")
        WORKER = "WORKER", _("Worker")

    objects: ClassVar[_UserManager] = _UserManager()

    public_id = models.UUIDField(editable=False, default=uuid.uuid4())

    role = models.CharField(choices=Role.choices, default=Role.WORKER, max_length=100)
