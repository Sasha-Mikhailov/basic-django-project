import logging
import json

from confluent_kafka import Consumer as KafkaConsumer

from app.settings import DEBUG, KAFKA_HOST, KAFKA_DRY_RUN


logger = logging.getLogger(__name__)

stdout = logger.info if DEBUG else print


class Consumer:
    conf = {
        'bootstrap.servers': KAFKA_HOST,
        'group.id': 'python_example_group_1',
        'auto.offset.reset': 'earliest'
    }
    def __init__(self, conf: dict=None, topics: list[str]= None, dry_run: bool=None):
        self.conf = conf or self.conf
        self.counts = {}
        self.dry_run = dry_run or KAFKA_DRY_RUN

        if not self.dry_run:
            self.consumer = KafkaConsumer(conf)

            if topics :
                self.subscribe(topics)

    def subscribe(self, topics: list[str]):
        self.counts.update = {
            topic_name: 0 for topic_name in topics
            if topic_name not in self.counts
        }
        if not self.dry_run:
            self.consumer.subscribe(topics)

    def poll(self, timeout:float=1.0):
        return self.consumer.poll(timeout)

    def close(self):
        self.consumer.close()

    @staticmethod
    def parse(msg):
        if msg is None:
            # No message available within timeout.
            # Initial message consumption may take up to
            # `session.timeout.ms` for the consumer group to
            # rebalance and start consuming
            print("Waiting for message or event/error in poll()")

        elif msg.error():
            print('error: {}'.format(msg.error()))

        else:
            # Check for Kafka message
            record_key = msg.key()
            record_value = msg.value()
            record_data = json.loads(record_value)
            count = record_data['count']
            print("Consumed record with key {} and value {}"
                  .format(record_key, record_value))

            return record_key, record_data
