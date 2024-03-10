from app.settings import Topics
from billing.api.serializers import BillingUserSerializer
from billing.models import BillingTask
from billing.models import BillingUser
from kafka_app.consumer import Consumer


class BillingTaskConsumer(Consumer):
    @staticmethod
    def do_work(record_key, record_data):
        payload = record_data.pop("payload")
        print(f"consumed message with key {record_key}; " f"meta {record_data}; " f"payload {payload}")

        if record_data["event_name"] == "tasks.task-created":
            # user = BillingTask.objects.update_or_create(
            #     public_id=payload["public_id"],
            #     assignee_public_id=payload["assignee_public_id"],
            #     status=payload["status"],
            #     title=payload["title"],
            # )

            task = BillingTask(
                public_id=payload["public_id"],
                assignee_public_id=payload["assignee_public_id"],
                title=payload["title"],
                status=payload["status"],
            )
            task.save()

            # task_serializer = BillingTaskSerializer(task)
            # task_serializer.is_valid()
            # task_serializer.save()


        elif record_data["event_name"] == "tasks.task-status-updated":
            task = BillingTask.objects.filter(public_id=payload["public_id"]).update(
                status=payload["new_status"],
            )
            print(f"updated task {task.public_id} with status {task.status}")

        elif record_data["event_name"] == "users.user-created":
            user = BillingUser.objects.update_or_create(
                public_id=payload["public_id"],
                role=payload["user_role"],
                first_name=payload["first_name"],
                last_name=payload["last_name"],
            )
            print(f"created BillingUser with pub_id {user.public_id} and role {user.role}")

        elif record_data["event_name"] == "users.user-updated":
            user = BillingUser.objects.filter(public_id=payload["public_id"]).update(
                role=payload["user_role"],
                first_name=payload["first_name"],
                last_name=payload["last_name"],
            )
            print(f"updated BillingUser with pub_id {user.public_id}")

        else:
            print(f"ignoring message with key `{record_key}` and meta `{record_data}`")


consumer = BillingTaskConsumer(group_id="billing_consumer")
consumer.subscribe(
    [
        Topics.tasks_stream,
        Topics.tasks,
        Topics.users_stream,
    ]
)


def start_billing_consumer():
    consumer.start_consuming(timeout=5.0)
