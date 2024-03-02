import random

from rest_framework import permissions, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from tasks.models import Task, TaskCost, TaskStatus, TaskUser
from tasks.api.serializers import TaskSerializer, TaskUserSerializer  #, TaskCostSerializer, TaskStatusSerializer


class TaskUserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = TaskUser.objects.all().order_by('-created')
    serializer_class = TaskUserSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]


class TaskViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows tasks to be viewed or edited.
    """
    queryset = Task.objects.all().order_by('-created')
    serializer_class = TaskSerializer
    # permission_classes = [permissions.IsAuthenticated]
    permission_classes = [permissions.AllowAny]

    @action(detail=False, methods=['post'], url_path='reassign', url_name='reassign', permission_classes=[permissions.AllowAny])
    def reassign_tasks(self, request):
        """
        get all tasks in progress and reassign them to a random worker
        """
        tasks_in_progress = Task.objects.filter(
            status=Task.Status.ASSIGNED
        )
        if len(tasks_in_progress) == 0:
            return Response({'status': 'No tasks with status=assigned available — nothing to reassign'})

        worker_users = TaskUser.objects.filter(role='worker')
        if len(worker_users) == 0:
            return Response({'status': 'No users with role=worker available; can\'t reassign tasks'})

        for task in tasks_in_progress:
            task.user = worker_users[random.randint(0, len(worker_users) - 1)]
            task.save()

        return Response({'status': f'{len(tasks_in_progress)} tasks reassigned'})
