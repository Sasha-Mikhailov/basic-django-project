import json
import logging

from confluent_kafka import Consumer as KafkaConsumer, KafkaError

from app.settings import DEBUG
from app.settings import KAFKA_DRY_RUN
from app.settings import KAFKA_HOST
from app.settings import KAFKA_CONSUME_TIMEOUT

logger = logging.getLogger(__name__)

stdout = logger.info if DEBUG else print


class Consumer:
    conf = {"bootstrap.servers": KAFKA_HOST, "group.id": "python_example_group_1", "auto.offset.reset": "earliest"}

    def __init__(self, conf: dict = None, topics: list[str] = None, dry_run: bool = None):
        self.conf = conf or self.conf
        self.counts = {}
        self.dry_run = dry_run or KAFKA_DRY_RUN

        if not self.dry_run:
            self.consumer = KafkaConsumer(self.conf)

            if topics:
                self.subscribe(topics)

    def subscribe(self, topics: list[str]):
        self.counts.update({topic_name: 0 for topic_name in topics if topic_name not in self.counts})
        if not self.dry_run:
            self.consumer.subscribe(topics)

    def poll(self, timeout: float = None):
        timeout = timeout or KAFKA_CONSUME_TIMEOUT
        return self.consumer.poll(timeout)

    def consume(self, **kwargs):
        timeout = kwargs.pop("timeout", None)
        msg = self.poll(timeout=timeout)

        if msg is None:
            if DEBUG:
                print(f"Waiting for message or event/error in poll() with timeout={timeout}s in topics {list(self.counts.keys())}")
            return

        elif msg.error():
            print("error: {}".format(msg.error()))
            raise KafkaError(msg.error())

        else:
            # Check for Kafka message
            record_key, record_data = self.parse(msg)

            self.do_work(record_key, record_data)

    def start_consuming(self, **kwargs):
        try:
            while True:
                self.consume(**kwargs)

        except KeyboardInterrupt:
            pass

        finally:
            # Leave group and commit final offsets
            self.close()

    def do_work(self, record_key, record_data):
        """override this method to implement the consumer's work"""
        raise NotImplementedError

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
            print("error: {}".format(msg.error()))

        else:
            # Check for Kafka message
            record_key = msg.key()
            record_value = msg.value()
            record_data = json.loads(record_value)

            return record_key, record_data
