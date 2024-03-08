from confluent_kafka import KafkaError

from app.conf import Topics
from billing.models import BillingTask
from billing.serializers import BillingTaskSerializer
from kafka_app.consumer import Consumer


def consume_tasks(consumer: Consumer):
    msg = consumer.poll(timeout_ms=1.0, max_records=200)

    if msg is None:
        # No message available within timeout.
        # Initial message consumption may take up to
        # `session.timeout.ms` for the consumer group to
        # rebalance and start consuming
        print("Waiting for message or event/error in poll()")
        return

    elif msg.error():
        print("error: {}".format(msg.error()))
        raise KafkaError(msg.error())

    else:
        # Check for Kafka message
        record_key, record_data = consumer.parse(msg)
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

        elif record_data["event_name"] == "tasks.status-updated":
            user = BillingTask.objects.filter(public_id=payload["public_id"]).update(
                status=payload["new_status"],
            )
            print(f"updated task {BillingTaskSerializer(user)}")

        else:
            print(f"ignoring message with key `{record_key}` and meta `{record_data}`")


consumer = Consumer()
consumer.subscribe([Topics.tasks_stream, Topics.tasks])

try:
    while True:
        consume_tasks(consumer)

except KeyboardInterrupt:
    pass

finally:
    # Leave group and commit final offsets
    consumer.close()
