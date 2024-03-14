from django.db import models

from app.models import TimestampedModel


class BillingUser(TimestampedModel):
    """
    replicates the User model from the Users app
    """

    public_id = models.UUIDField(unique=True)

    role = models.CharField(
        max_length=100,
        default="WORKER",
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.public_id}"

    def save(self, *args, **kwargs):
        super(BillingUser, self).save(*args, **kwargs)
        # only for new users
        if not self.pk:
            account = BillingAccount.objects.update_or_create(user=self)
            print(f"created account for user {self} with balance {account}")


class BillingAccount(TimestampedModel):
    """
    account for each user to keep track of deposits and withdrawals
    """

    user = models.ForeignKey(BillingUser, on_delete=models.CASCADE, unique=True, blank=False, null=False)

    balance = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        blank=False,
        null=False,
    )
