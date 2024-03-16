from rest_framework import serializers

from billing.models import BillingTask
from billing.models import BillingTransaction
from billing.models import BillingUser


class BillingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingUser
        fields = "__all__"


class BillingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingTask
        fields = "__all__"


class BillingTransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingTransaction
        fields = "__all__"
