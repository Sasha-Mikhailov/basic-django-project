from rest_framework import serializers

from tasks.models import Task, TaskCost, TaskStatus, TaskUser


class TaskUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = TaskUser
        # fields = ['url', 'username', 'email', 'groups']
        fields = '__all__'


class TaskSerializer(serializers.ModelSerializer):
    # user = TaskUserSerializer(many=False)
    user = serializers.StringRelatedField(many=False)
    status = serializers.StringRelatedField(many=False)

    class Meta:
        model = Task
        # fields = []
        fields = '__all__'

    def create(self, validated_data):
        user_data = validated_data.pop('user')
        user = TaskUser.objects.get_or_create(**user_data)
        task_status = TaskStatus.objects.get_or_create(status=TaskStatus.Status.ASSIGNED)
        task = Task.objects.create(user=user, status=task_status, **validated_data)
        return task