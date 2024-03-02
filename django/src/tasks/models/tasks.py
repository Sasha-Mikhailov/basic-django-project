import uuid
import random

from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import DefaultModel, TimestampedModel


class TaskUser(TimestampedModel):
    public_id = models.UUIDField() # editable=False

    role = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.role}'


class Task(TimestampedModel):
    public_id = models.UUIDField(editable=False, default=uuid.uuid4())

    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(TaskUser, on_delete=models.CASCADE, blank=False, null=False)

    cost_assign = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=random.randint(1000, 2000) / 100,
        editable=False,
        blank=False, null=False,
    )
    cost_complete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=random.randint(2000, 4000) / 100,
        blank=False, null=False,
    )

    class Status(models.TextChoices):
        ASSIGNED = 'ASSIGNED', _('Assigned')
        COMPLETED = 'COMPLETED', _('Completed')

    status = models.CharField(
        default=Status.ASSIGNED,
        choices=Status.choices,
        max_length=100,
    )

    def __str__(self):
        return self.title


# FIXME failed to implement creation within Task model/serializer
class TaskCost(TimestampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    cost_assign = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=random.randint(1000, 2000) / 100
    )
    cost_complete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=random.randint(2000, 4000) / 100
    )

    def __str__(self):
        return f'{self.task.title} - {self.cost}'


# FIXME failed to implement creation within Task model/serializer
class TaskStatus(TimestampedModel):
    class Status(models.TextChoices):
        ASSIGNED = 'ASSIGNED', _('Assigned')
        COMPLETED = 'COMPLETED', _('Completed')

    status = models.CharField(
        default=Status.ASSIGNED,
        choices=Status.choices,
        max_length=100,
    )
    task = models.ForeignKey(Task, on_delete=models.CASCADE)

    def __str__(self):
        return self.status