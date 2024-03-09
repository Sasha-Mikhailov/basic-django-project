from app.settings import Topics
from billing.api.serializers import BillingTaskSerializer
from billing.models import BillingTask
from kafka_app.consumer import Consumer


class BillingTaskConsumer(Consumer):
    @staticmethod
    def do_work(record_key, record_data):
        payload = record_data.pop("payload")

        print(f"consumed message with key {record_key}; " f"meta {record_data}; " f"payload {payload}")

        if record_data["event_name"] == "tasks.task-created":
            user = BillingTask.objects.update_or_create(
                public_id=payload["public_id"],
                assignee_public_id=payload["assignee_public_id"],
                status=payload["status"],
                title=payload["title"],
            )
            print(f"created task {BillingTaskSerializer(user)}")

        elif record_data["event_name"] == "tasks.task-status-updated":
            user = BillingTask.objects.filter(public_id=payload["public_id"]).update(
                status=payload["new_status"],
            )
            print(f"updated task {BillingTaskSerializer(user)}")

        else:
            print(f"ignoring message with key `{record_key}` and meta `{record_data}`")


btc = BillingTaskConsumer()
btc.subscribe(
    [
        Topics.tasks_stream,
        Topics.tasks,
    ]
)

def consume_billing_tasks():
    btc.start_consuming(timeout=5.0)
