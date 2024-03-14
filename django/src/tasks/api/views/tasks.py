from datetime import datetime
import random
import uuid

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from app.settings import Topics
from kafka_app.producer import Producer
from tasks.api.serializers import TaskSerializer
from tasks.models import Task
from tasks.models import TaskUser

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

    queryset = Task.objects.all().order_by("-created")
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        user_data = serializer.validated_data.get("user")

        if not user_data:
            worker_users = TaskUser.objects.filter(role="WORKER")
            user = worker_users[random.randint(0, len(worker_users) - 1)]
        else:
            user = TaskUser.objects.get(**user_data)

        serializer.save(user=user)

        event = {
            "event_id": str(uuid.uuid4()),
            "event_version": "1",
            "event_name": "tasks.task-created",
            "event_time": datetime.now().isoformat(),
            "producer": "tasks-service",
            "payload": {
                "public_id": str(serializer.data["public_id"]),
                "created": str(serializer.data["created"]),
                "title": str(serializer.data["title"]),
                "description": str(serializer.data["description"]),
                "assignee_public_id": str(user.public_id),
                "status": str(serializer.data["status"]),
            },
        }

        # CUD event: task created
        p.produce(topic=Topics.tasks_stream, key=event["event_id"], value=event)

    def perform_update(self, serializer):
        old_status = serializer.instance.status
        new_status = serializer.validated_data.get("status", old_status)

        serializer.save(**serializer.validated_data)
        if old_status != new_status:
            event = {
                "event_id": str(uuid.uuid4()),
                "event_version": "1",
                "event_name": "tasks.task-status-updated",
                "event_time": datetime.now().isoformat(),
                "producer": "tasks-service",
                "payload": {
                    "public_id": str(serializer.data["public_id"]),
                    "old_status": str(old_status),
                    "new_status": str(new_status),
                },
            }

            # business event: status changed
            p.produce(topic=Topics.tasks, key=event["event_id"], value=event)

    @action(detail=False, methods=["post"], url_path="reassign", url_name="reassign", permission_classes=[permissions.IsAdminUser])
    def reassign_tasks(self, request):
        """
        get all tasks in progress and reassign them to a random worker
        """
        print("reassign_tasks")
        tasks_in_progress = Task.objects.filter(status=Task.Status.ASSIGNED)
        if len(tasks_in_progress) == 0:
            return Response({"status": "No tasks with status=assigned available — nothing to reassign"})

        worker_users = TaskUser.objects.filter(role="WORKER")
        if len(worker_users) == 0:
            return Response({"status": "No users with role=worker available; can't reassign tasks"})

        for task in tasks_in_progress:
            new_assignee = worker_users[random.randint(0, len(worker_users) - 1)]
            task.user = new_assignee

            event = {
                "event_id": str(uuid.uuid4()),
                "event_version": "1",
                "event_name": "tasks.task-reassigned",
                "event_time": datetime.now().isoformat(),
                "producer": "tasks-service",
                "payload": {
                    "public_id": str(task.public_id),
                    "new_assignee_public_id": str(new_assignee.public_id),
                    # just in case ↓
                    "title": str(task.title),
                    "description": str(task.description),
                    "status": str(task.status),
                },
            }

            # business event: status changed
            p.produce(topic=Topics.tasks_stream, key=event["event_id"], value=event)

        tasks_in_progress.bulk_update(tasks_in_progress, ["user"])

        return Response({"status": f"{len(tasks_in_progress)} tasks reassigned"})
