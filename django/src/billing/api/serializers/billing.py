from rest_framework import serializers

from django.db import transaction

from billing.models import BillingAccount
from billing.models import BillingTask
from billing.models import BillingUser


class BillingUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingUser
        fields = "__all__"

    def create(self, validated_data):
        with transaction.atomic():
            user = BillingUser.objects.create_or_update(
                public_id=validated_data["public_id"],
                role=validated_data["role"],
                first_name=validated_data["first_name"],
                last_name=validated_data["last_name"],
            )
            account = BillingAccount.objects.create_or_update(user=user)

        return user


class BillingTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = BillingTask
        fields = "__all__"

    def create(self, validated_data):
        task = BillingTask.objects.create_or_update(
            public_id=validated_data["public_id"],
            assignee_public_id=validated_data["assignee_public_id"],
            status=validated_data["status"],
        )

        print(f"task created: {task}")
        print(f"cost assigned: {task.cost_assign}")
        print(f"cost complete: {task.cost_complete}")

        # TODO task assigned = withdraw from user account cost_assigned

        return task

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        task = BillingTask.update_or_create(**instance.data)

        # catch re-assignment of the task
        old_assignee = instance.assignee_public_id
        new_assignee = validated_data.assignee_public_id

        old_assigned = instance.status == BillingTask.status.ASSIGNED
        new_assigned = validated_data.status == BillingTask.status.ASSIGNED

        task_reassigned = (old_assignee != new_assignee) & (old_assigned & new_assigned)
        # TODO task re-assigned = withdraw from user account cost_assigned
        # ...

        # catch completion of the task
        new_completed = validated_data.status == BillingTask.status.COMPLETED
        task_completed = old_assigned & new_completed
        # TODO task completed = deposit to user account cost_complete
        # ...

        return task
