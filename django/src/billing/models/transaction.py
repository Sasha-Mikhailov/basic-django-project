from datetime import datetime
import uuid

from rest_framework.exceptions import ValidationError

from django.db import models
from django.utils.translation import gettext_lazy as _

from billing.models.user import BillingAccount

from app.models import TimestampedModel
from app.settings import Topics
from kafka_app.producer import Producer

p = Producer()


class BillingTransaction(TimestampedModel):
    """
    id, account_id, desc, type, credit, debit
    """

    id = models.AutoField(primary_key=True)

    # just a simplification, in reality this would be a foreign key to a BillingCycle
    # assuming that we have the only one cycle for each user — daily cash out
    billing_cycle_id = models.DateField(default=datetime.today, blank=False, null=False)

    account = models.ForeignKey(BillingAccount, on_delete=models.CASCADE, blank=False, null=False)

    description = models.CharField(max_length=100)

    class TransactionType(models.TextChoices):
        DEPOSIT = "DEPOSIT", _("Deposit")
        WITHDRAWAL = "WITHDRAWAL", _("Withdrawal")
        PAYMENT = "PAYMENT", _("Payment")

    type = models.CharField(
        choices=TransactionType.choices,
        max_length=100,
        blank=False,
        null=False,
    )

    credit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=False,
        null=False,
    )

    debit = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=False,
        null=False,
    )

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValidationError(f"Transaction are immutable, cannot be updated or deleted.")

        print(f"saving transaction {self.description} with type {self.type} and amount {self.credit or self.debit}")
        super(BillingTransaction, self).save(*args, **kwargs)

        event = {
            "event_id": str(uuid.uuid4()),
            "event_version": "1",
            "event_name": "billing.transaction-created",
            "event_time": datetime.now().isoformat(),
            "producer": "billing-service",
            "payload": {
                "tx_id": str(self.id),
                "tx_type": str(self.type),
                "billing_cycle": str(self.billing_cycle_id),
                "account": str(self.account),
                "credit": str(self.credit),
                "debit": str(self.debit),
                # just in case
                "description": str(self.description),
            },
        }

        p.produce(topic=Topics.billing_tx, key=event["event_id"], value=event)
