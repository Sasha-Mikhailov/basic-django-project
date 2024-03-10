from app.admin import admin
from app.admin import ModelAdmin
from billing.models import BillingAccount
from billing.models import BillingTask
from billing.models import BillingUser


@admin.register(BillingUser, BillingAccount, BillingTask)
class TaskAdmin(ModelAdmin):
    pass
