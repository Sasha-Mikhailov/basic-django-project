import random
import json

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tasks.models import Task, TaskCost, TaskStatus, TaskUser
from tasks.api.serializers import TaskSerializer, TaskUserSerializer
from tasks.producer import Producer

from tasks.tests.mock import produce  # FIXME change for real kafka producer



# FIXME users can't be created here, only replicated via kafka
# class TaskUserViewSet(viewsets.ModelViewSet):
#     """
#     API endpoint that allows users to be viewed or edited.
#     """
#     queryset = TaskUser.objects.all().order_by('-created')
#     serializer_class = TaskUserSerializer
#     # FIXME change to IsAuthenticated
#     permission_classes = [permissions.AllowAny]

p = Producer()

class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    queryset = Task.objects.all().order_by('-created')
    serializer_class = TaskSerializer
    # FIXME change to IsAuthenticated
    permission_classes = [permissions.AllowAny]


    def perform_create(self, serializer):
        user_data = serializer.validated_data.get('user')

        if not user_data:
            worker_users = TaskUser.objects.filter(role='worker')
            user = worker_users[random.randint(0, len(worker_users) - 1)]
        else:
            user = TaskUser.objects.get(**user_data)

        serializer.save(user=user)
        # CUD event: task created
        p.produce(topic='tasks-stream', key='task-created', value=json.dumps(serializer.data))

    def perform_update(self, serializer):
        initial_status = serializer.instance.status
        new_status = serializer.validated_data.get('status', initial_status)

        serializer.save(**serializer.validated_data)
        if initial_status != new_status:
            # business event: status changed
            p.produce(topic='tasks', key='task-status-updated', value=json.dumps(serializer.data))

    # FIXME change permissions to IsAdmin
    @action(detail=False, methods=['post'], url_path='reassign', url_name='reassign', permission_classes=[permissions.AllowAny])
    def reassign_tasks(self, request):
        """
        get all tasks in progress and reassign them to a random worker
        """
        print('reassign_tasks')
        tasks_in_progress = Task.objects.filter(
            status=Task.Status.ASSIGNED
        )
        if len(tasks_in_progress) == 0:
            return Response({'status': 'No tasks with status=assigned available — nothing to reassign'})

        worker_users = TaskUser.objects.filter(role='worker')
        if len(worker_users) == 0:
            return Response({'status': 'No users with role=worker available; can\'t reassign tasks'})

        # TODO use bulk update here
        for task in tasks_in_progress:
            task.user = worker_users[random.randint(0, len(worker_users) - 1)]
            task.save()

        return Response({'status': f'{len(tasks_in_progress)} tasks reassigned'})
