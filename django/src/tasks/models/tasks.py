import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel


class TaskUser(TimestampedModel):
    public_id = models.UUIDField(unique=True)

    role = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.public_id}'


class Task(TimestampedModel):
    public_id = models.UUIDField(unique=True, editable=False, default=uuid.uuid4)

    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(TaskUser, on_delete=models.CASCADE, blank=False, null=False)

    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", _("Assigned")
        COMPLETED = "COMPLETED", _("Completed")

    status = models.CharField(
        default=Status.ASSIGNED,
        choices=Status.choices,
        max_length=100,
    )

    def __str__(self):
        return f'{self.public_id}'
