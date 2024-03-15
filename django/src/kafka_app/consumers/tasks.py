from django.db.utils import IntegrityError

from app.settings import Topics
from kafka_app.consumer import Consumer
from tasks.models import TaskUser


class TasksUserConsumer(Consumer):
    def do_work(self, record_key, record_data):
        payload = record_data.pop("payload")
        print(f"consumed message with key {record_key}; " f"meta {record_data}; " f"payload {payload}")

        try:
            if record_data["event_name"] == "users.user-created":
                user, _ = TaskUser.objects.update_or_create(
                    public_id=payload["public_id"],
                    created=payload["created"],
                    role=payload["user_role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
                print(f"created user {user} with public_id {payload['public_id']}")

            elif record_data["event_name"] == "users.user-updated":
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
            # TODO add DLQ for failed messages

            print(f"\n\t >>> ERROR processing message with key `{record_key}` and meta `{record_data}`\n\n {e}\n")
            raise e


consumer = TasksUserConsumer(group_id="tasks_consumer")
consumer.subscribe([Topics.users_stream])


def start_consumer_tasks():
    consumer.start_consuming(timeout=5.0)
