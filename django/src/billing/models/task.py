from datetime import datetime
import random
import uuid

from django.db import models
from django.db import transaction as db_transaction
from django.utils.translation import gettext_lazy as _

from app.models import TimestampedModel
from app.settings import Topics
from billing.models.transaction import BillingTransaction
from billing.models.user import BillingAccount
from billing.models.user import BillingUser
from kafka_app.producer import Producer

p = Producer()


def get_assign_cost():
    return random.randint(1000, 2000) / 100


def get_complete_cost():
    return random.randint(2000, 4000) / 100


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
        return f"{self.public_id}"

    def save(self, *args, **kwargs):
        print(f"saving task {self.public_id}")

        with db_transaction.atomic():
            if not BillingUser.objects.filter(public_id=self.assignee_public_id).exists():
                user = BillingUser(public_id=self.assignee_public_id)
                user.save()
            else:
                user = BillingUser.objects.get(public_id=self.assignee_public_id)

            if not BillingAccount.objects.filter(user=user).exists():
                account = BillingAccount.objects.create(user=user)
            else:
                account = BillingAccount.objects.get(user=user)

            if not self.pk:
                print("creating new task")
                # make withdrawal on creation
                transaction = BillingTransaction.objects.create(
                    billing_cycle_id=datetime.today(),
                    account=account,
                    description=f"Task {self.public_id} assigned",
                    type=BillingTransaction.TransactionType.WITHDRAWAL,
                    credit=self.cost_assign,
                )
                print(f"withdrew {self.cost_assign} from {user} for task {self.public_id} assigned")

                # just a shortcut to get the current balance later
                BillingAccount.objects.filter(user=user).update(balance=models.F("balance") - self.cost_assign)

            else:
                # catch re-assignment of the task
                old_assignee = BillingTask.objects.get(pk=self.pk).assignee_public_id
                new_assignee = self.assignee_public_id

                old_status_assigned = BillingTask.objects.get(pk=self.pk).status == str(BillingTask.Status.ASSIGNED)
                new_status_assigned = self.status == str(BillingTask.Status.ASSIGNED)

                task_reassigned = (old_assignee != new_assignee) & (old_status_assigned & new_status_assigned)

                # catch completion of the task
                old_status_assigned = BillingTask.objects.get(pk=self.pk).status == BillingTask.Status.ASSIGNED
                new_status_completed = self.status == BillingTask.Status.COMPLETED

                task_completed = old_status_assigned & new_status_completed

                if task_reassigned:
                    # make withdrawal on re-assignment
                    transaction = BillingTransaction.objects.create(
                        billing_cycle_id=datetime.today(),
                        account=account,
                        description=f"Task {self.public_id} re-assigned",
                        type=BillingTransaction.TransactionType.WITHDRAWAL,
                        credit=self.cost_assign,
                    )
                    BillingAccount.objects.filter(user=user).update(balance=models.F("balance") - self.cost_assign)

                    print(f"withdrew {self.cost_assign} from {user} for task {self.public_id} re-assigned")

                elif task_completed:
                    # make deposit on completion
                    transaction = BillingTransaction.objects.create(
                        billing_cycle_id=datetime.today(),
                        account=account,
                        description=f"Task {self.public_id} completed",
                        type=BillingTransaction.TransactionType.DEPOSIT,
                        debit=self.cost_complete,
                    )
                    BillingAccount.objects.filter(user=user).update(balance=models.F("balance") + self.cost_complete)
                    print(f"deposited {self.cost_complete} to {user} for task {self.public_id} completed")

            super(BillingTask, self).save(*args, **kwargs)

        event = {
            "event_id": str(uuid.uuid4()),
            "event_version": "1",
            "event_name": "billing.task-created",
            "event_time": datetime.now().isoformat(),
            "producer": "billing-service",
            "payload": {
                "public_id": str(self.public_id),
                "created": str(self.created),
                "assignee_public_id": str(self.assignee_public_id),
                "cost_assign": str(self.cost_assign),
                "cost_complete": str(self.cost_complete),
            },
        }

        p.produce(topic=Topics.billing_tasks, key=event["event_id"], value=event)
