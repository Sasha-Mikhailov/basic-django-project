from confluent_kafka import KafkaError

from app.consumer import Consumer
from app.models import TaskUser
from app.producer import Topics
from app.serializers import TaskUserSerializer

consumer = Consumer()
consumer.subscribe([Topics.users_stream])
total_count = 0

try:
    while True:
        msg = consumer.poll(timeout_ms=1.0, max_records=200)
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to
            # `session.timeout.ms` for the consumer group to
            # rebalance and start consuming
            print("Waiting for message or event/error in poll()")
            continue
        elif msg.error():
            print("error: {}".format(msg.error()))
            raise KafkaError(msg.error())
        else:
            # Check for Kafka message
            record_key, record_data = consumer.parse(msg)

            print(f"consumed message with key {record_key} and value {record_data}")

            payload = record_key.get("payload", {})

            if record_key == "users.user-created":
                user = TaskUser.objects.update_or_create(
                    public_id=payload["public_id"],
                    role=payload["user_role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
                print(f"created user {TaskUserSerializer(user)}")
            elif record_key == "users.user-updated":
                user = TaskUser.objects.filter(public_id=payload["public_id"]).update(
                    role=payload["user_role"],
                    first_name=payload["first_name"],
                    last_name=payload["last_name"],
                )
                print(f"updated user {TaskUserSerializer(user)}")
            else:
                print(f"ignoring message with key `{record_key}` and payload `{payload}`")

except KeyboardInterrupt:
    pass

finally:
    # Leave group and commit final offsets
    consumer.close()
