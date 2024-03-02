import random

from rest_framework import serializers

from tasks.models import Task, TaskCost, TaskStatus, TaskUser

from tasks.tests.mock import produce


class TaskUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUser
        # fields = ['url', 'username', 'email', 'groups']
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(many=False)

    class Meta:
        model = Task
        fields = '__all__'  # ['public_id', 'title', 'description', 'user', 'status', 'cost_assign', 'cost_complete']
