from django.db.utils import IntegrityError

from analytics.models import ATask
from analytics.models import ATaskLog
from analytics.models import ATransaction
from analytics.models import ATransactionLog
from analytics.models import AUser
from app.settings import Topics
from kafka_app.consumer import Consumer

TASKS_EVENTS = frozenset(["tasks.task-created", "tasks.task-completed", "billing.task-created"])

BILLING_EVENTS = frozenset(["billing.transaction-created"])


def parse_payload_for_event_log(payload):
    return dict(
        event_id=payload["event_id"],
        created=payload["event_time"],
        event_version=payload["event_version"],
        producer=payload["producer"],
        event_name=payload["event_name"],  # keep the event meta to scan events in db
        payload=payload["payload"],  # dump the whole payload as json string no matter the schema
    )


class AnalyticsConsumer(Consumer):
    def do_work(self, record_key, record_data):
        payload = record_data.get("payload", {})
        print(f"consumed message with key {record_key}; " f"meta {record_data}; " f"payload {payload}")

        try:
            if (record_data["event_name"] == "tasks.task-created") & (str(record_data["event_version"]) == "1"):
                task, created = ATask.objects.update_or_create(
                    public_id=payload["public_id"],
                    defaults={
                        "created": payload["created"],
                        "assignee_public_id": payload["assignee_public_id"],
                        "title": payload["title"],
                        "status": payload["status"],
                    },
                )
                print(f"created task {task} with status {task}")

            elif (record_data["event_name"] == "tasks.task-completed") & (str(record_data["event_version"]) == "1"):
                task, created = ATask.objects.update_or_create(
                    public_id=payload["public_id"],
                    defaults={
                        "created": payload["created"],
                        "status": payload["new_status"],
                    },
                )
                print(f"updated task {task} with status {payload['new_status']}")

            elif (record_data["event_name"] == "billing.task-created") & (str(record_data["event_version"]) == "1"):
                task, created = ATask.objects.update_or_create(
                    public_id=payload["public_id"],
                    defaults={
                        "created": payload["created"],
                        "assignee_public_id": payload["assignee_public_id"],
                        "cost_assign": payload["cost_assign"],
                        "cost_complete": payload["cost_complete"],
                    },
                )
                print(f"consumed ATask with pub_id {task.public_id}")

            elif (record_data["event_name"] == "users.user-created") & (str(record_data["event_version"]) == "1"):
                user = AUser(
                    public_id=payload["public_id"],
                    created=payload["created"],
                    role=payload["user_role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
                user.save()
                print(f"created AUser with pub_id {user.public_id}")

            elif (record_data["event_name"] == "users.user-updated") & (str(record_data["event_version"]) == "1"):
                user = AUser.objects.get(public_id=payload["public_id"])
                user.role = payload["user_role"]
                user.first_name = payload["first_name"]
                user.last_name = payload["last_name"]
                user.save()
                print(f"updated AUser with pub_id {user.public_id}")

            elif (record_data["event_name"] == "billing.transaction-created") & (str(record_data["event_version"]) == "1"):
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
                    },
                )

                print(f"consumed ATransaction with tx_id {tx.tx_id}")

            else:
                print(f"ignoring message with key `{record_key}` and meta `{record_data}`")

            # just put into the DB every event and let the data pipelines handle the rest
            # (instead of DLQ mechanism for the sake of durability)
            if record_data["event_name"] in TASKS_EVENTS:
                log_record = ATaskLog.objects.create(**parse_payload_for_event_log(record_data))

            elif record_data["event_name"] in BILLING_EVENTS:
                log_record = ATransactionLog.objects.create(**parse_payload_for_event_log(record_data))

        except IntegrityError as e:
            print(f"seems already consumed event with key `{record_key}` and meta `{record_data}`")

        except Exception as e:
            print(f"\n\t >>> ERROR processing message with key `{record_key}` and meta `{record_data}`\n\n {e}\n")
            raise e


consumer = AnalyticsConsumer(group_id="analytics_consumer")
consumer.subscribe(
    [
        Topics.users_stream,
        Topics.tasks_stream,
        Topics.tasks,
        Topics.billing_tasks,
        Topics.billing_tx,
    ]
)


def start_analytics_consumer():
    consumer.start_consuming(timeout=5.0)
