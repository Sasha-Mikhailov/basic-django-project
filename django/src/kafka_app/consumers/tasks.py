from django.db.utils import IntegrityError

from app.settings import DEBUG
from app.settings import Topics
from kafka_app.consumer import Consumer
from kafka_app.producer import Producer
from tasks.models import TaskUser

p = Producer()


class TasksUserConsumer(Consumer):
    def do_work(self, record_key, record_data):
        payload = record_data.pop("payload")
        print(f"consumed message with key {record_key}; " f"meta {record_data}; " f"payload {payload}")

        try:
            if (record_data["event_name"] == "users.user-created") & (str(record_data["event_version"]) == "1"):
                user, _ = TaskUser.objects.update_or_create(
                    public_id=payload["public_id"],
                    created=payload["created"],
                    role=payload["user_role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
                print(f"created user {user} with public_id {payload['public_id']}")

            elif (record_data["event_name"] == "users.user-updated") & (str(record_data["event_version"]) == "1"):
                user = TaskUser.objects.filter(public_id=payload["public_id"]).update(
                    role=payload["user_role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
                print(f"updated user {user}")

            else:
                print(f"ignoring message with key `{record_key}` and payload `{payload}`")

        except IntegrityError as e:
            print(f"seems already consumed event with key `{record_key}` and meta `{record_data}`")

        except Exception as e:
            # DLQ for failed messages
            event_seen = record_data.get("event_seen_times", 0)
            record_data.update(
                {
                    "event_seen_times": event_seen + 1,
                    "last_error": str(e),
                }
            )
            p.produce(topic=Topics.billing_dlq, key=record_data["event_id"], value=record_data)
            # TODO add DLQ consumer logic (somewhere?)

            if DEBUG:
                print(f"\n\t >>> ERROR processing message with key `{record_key}` and meta `{record_data}`\n\n {e}\n")
                raise e
            else:
                # ACK the message to avoid re-processing
                self.commit()


consumer = TasksUserConsumer(group_id="tasks_consumer")
consumer.subscribe([Topics.users_stream])


def start_consumer_tasks():
    consumer.start_consuming(timeout=5.0)
