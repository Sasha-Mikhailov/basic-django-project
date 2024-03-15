from tenacity import retry
from tenacity import retry_if_exception_type
from tenacity import wait_exponential

from django.db.utils import OperationalError

from app.settings import Topics
from analytics.models import AUser
from analytics.models import ATask
from analytics.models import ATransaction
from kafka_app.consumer import Consumer


class AnalyticsConsumer(Consumer):
    @retry(
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type(OperationalError),
    )
    def do_work(self, record_key, record_data):
        payload = record_data.get("payload", {})
        print(f"consumed message with key {record_key}; " f"meta {record_data}; " f"payload {payload}")

        try:
            if record_data["event_name"] == "tasks.task-created":
                task, created = ATask.objects.update_or_create(
                    public_id=payload["public_id"],
                    defaults={
                        "created": payload["created"],
                        "assignee_public_id": payload["assignee_public_id"],
                        "title": payload["title"],
                        "status": payload["status"],
                })
                print(f"created task {task} with status {task}")


            elif record_data["event_name"] == "tasks.task-completed":
                task, created = ATask.objects.update_or_create(
                    public_id=payload["public_id"],
                    defaults={
                        'created': payload["created"],
                        'status': payload["new_status"],
                    })
                print(f"updated task {task} with status {payload['new_status']}")


            elif record_data["event_name"] == "billing.task-created":
                task, created = ATask.objects.update_or_create(
                    public_id=payload["public_id"],
                    defaults={
                        "created": payload["created"],
                        "assignee_public_id": payload["assignee_public_id"],
                        "cost_assign": payload["cost_assign"],
                        "cost_complete": payload["cost_complete"],
                    }
                )
                print(f"consumed ATask with pub_id {task.public_id}")

            elif record_data["event_name"] == "users.user-created":
                user = AUser(
                    public_id=payload["public_id"],
                    created=payload["created"],
                    role=payload["user_role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
                user.save()
                print(f"created AUser with pub_id {user.public_id}")

            elif record_data["event_name"] == "users.user-updated":
                user = AUser.objects.get(public_id=payload["public_id"])
                user.role = payload["user_role"]
                user.first_name = payload["first_name"]
                user.last_name = payload["last_name"]
                user.save()
                print(f"updated AUser with pub_id {user.public_id}")

            elif record_data["event_name"] == "billing.transaction-created":
                tx, created = ATransaction.objects.update_or_create(
                    tx_id=payload["tx_id"],
                    defaults={
                        "type": payload["tx_type"],
                        "created": payload["created"],
                        "billing_cycle_id": payload["billing_cycle"][:10],
                        "account": payload["account"],
                        "credit": payload["credit"],
                        "debit": payload["debit"],
                        "description": payload["description"],
                    }
                )

                print(f"consumed ATransaction with tx_id {tx.tx_id}")

            else:
                print(f"ignoring message with key `{record_key}` and meta `{record_data}`")

        except Exception as e:
            # TODO add DLQ for failed messages

            print(f"\n\t >>> ERROR processing message with key `{record_key}` and meta `{record_data}`\n\n {e}\n")
            raise e


consumer = AnalyticsConsumer(group_id="analytics_consumer")
consumer.subscribe(
    [
        Topics.tasks_stream,
        Topics.tasks,
        Topics.users_stream,
        Topics.billing_tasks,
        Topics.billing_tx,
    ]
)


def start_analytics_consumer():
    consumer.start_consuming(timeout=5.0)
