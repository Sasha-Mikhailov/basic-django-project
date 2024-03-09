from django.db import models
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel


def get_assign_cost():
    import random

    return random.randint(1000, 2000) / 100


def get_complete_cost():
    import random

    return random.randint(2000, 4000) / 100


class BillingUser(TimestampedModel):
    """
    replicates the User model from the Users app
    """

    public_id = models.UUIDField(unique=True)

    role = models.CharField(max_length=100)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.role}"


class BillingAccount(TimestampedModel):
    """
    account for each user to keep track of deposits and withdrawals
    """

    user = models.ForeignKey(BillingUser, on_delete=models.CASCADE, blank=False, null=False)

    # TODO transaction_id, amount?

    # TODO add bank account details for user to arrange payments via bank transfer


class BillingTask(TimestampedModel):
    """
    replicates the Tasks model from the Tasks app
    and generates costs for each task on insert into the database
    """

    class Status(models.TextChoices):
        ASSIGNED = "ASSIGNED", _("Assigned")
        COMPLETED = "COMPLETED", _("Completed")

    public_id = models.UUIDField(unique=True, blank=False, null=False)

    assignee_public_id = models.UUIDField(blank=False, null=False)

    status = models.CharField(
        max_length=100,
        blank=False,
        null=False,
    )

    cost_assign = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=get_assign_cost,
        editable=False,  # only the system can set the cost
        blank=False,
        null=False,
    )

    cost_complete = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=get_complete_cost,
        editable=False,  # only the system can set the cost
        blank=False,
        null=False,
    )

    # just in case (not needed for billing per se)
    title = models.CharField(
        max_length=100,
    )

    def __str__(self):
        return f"{self.public_id} - assign: ${self.cost_assign}, complete: ${self.cost_complete}"


# ???????????????
# TODO add Billing Cycle
# TODO add Transaction
# TODO add Payment
# ???????????????
