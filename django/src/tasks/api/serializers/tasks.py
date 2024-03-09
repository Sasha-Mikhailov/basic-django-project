import uuid

from rest_framework import serializers

from tasks.models import Task
from tasks.models import TaskUser


class TaskUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUser
        # fields = ['url', 'username', 'email', 'groups']
        fields = "__all__"


class TaskSerializer(serializers.ModelSerializer):
    public_id = serializers.UUIDField(
        read_only=True,
        default=serializers.CreateOnlyDefault(uuid.uuid4()),
    )
    user = serializers.StringRelatedField(many=False)

    class Meta:
        model = Task
        fields = "__all__"  # ['public_id', 'title', 'description', 'user', 'status', 'cost_assign', 'cost_complete']
