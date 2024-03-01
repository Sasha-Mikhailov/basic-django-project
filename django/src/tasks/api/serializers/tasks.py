from rest_framework import serializers

from tasks.models import Task, TaskCost, TaskStatus, TaskUser


class TaskUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUser
        # fields = ['url', 'username', 'email', 'groups']
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        # fields = ['url', 'username', 'email', 'groups']
        fields = '__all__'
