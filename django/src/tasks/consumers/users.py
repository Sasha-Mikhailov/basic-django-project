import json

from confluent_kafka import KafkaError

from app.models import TaskUser
from app.serializers import TaskUserSerializer

from app.consumer import Consumer
from app.producer import Topics


consumer = Consumer()
consumer.subscribe([Topics.users_stream])
total_count = 0

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to
            # `session.timeout.ms` for the consumer group to
            # rebalance and start consuming
            print("Waiting for message or event/error in poll()")
            continue
        elif msg.error():
            print('error: {}'.format(msg.error()))
            raise KafkaError(msg.error())
        else:
            # Check for Kafka message
            record_key, record_data = consumer.parse(msg)
            # do not 'import' other db internal ids (just in case)
            _ = record_data.pop('id')

            print(f'consumed message with key {record_key} and value {record_data}')

            # TODO create or update user by public_id
            if record_key == 'user-created':
                user = TaskUser.objects.update_or_create(**record_data)
                print(f'created user {TaskUserSerializer(user)}')
            elif record_key == 'user-updated':
                user = TaskUser.objects.filter(public_id=record_data['public_id']).update(**record_data)
                print(f'updated user {TaskUserSerializer(user)}')
            else:
                print(f'ignoring message with key {record_key}')

except KeyboardInterrupt:
    pass

finally:
    # Leave group and commit final offsets
    consumer.close()