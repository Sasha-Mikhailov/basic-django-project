from rest_framework import permissions, viewsets

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
