import uuid

from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import DefaultModel, TimestampedModel

# Rename this file to singular form of your entity, e.g. "orders.py -> order.py". Add your class to __init__.py.


class TaskUser(TimestampedModel):
    # user = models.ForeignKey('users.User', on_delete=models.CASCADE)
    public_id = models.UUIDField() # editable=False

    role = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f'{self.first_name} {self.last_name} - {self.role}'


class Task(TimestampedModel):
    title = models.CharField(max_length=100)
    description = models.TextField()
    user = models.ForeignKey(TaskUser, on_delete=models.CASCADE)

    def __str__(self):
        return self.title


class TaskCost(TimestampedModel):
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    cost = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.task.title} - {self.cost}'


class TaskStatus(TimestampedModel):
    class Status(models.TextChoices):
        ASSIGNED = 'ASSIGNED', _('Assigned')
        COMPLETED = 'COMPLETED', _('Completed')

    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    status = models.CharField(
        choices=Status.choices,
        max_length=100,
    )

    def __str__(self):

        return self.status