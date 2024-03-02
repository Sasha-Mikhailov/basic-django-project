import enum
import logging

from app.settings import DEBUG

from confluent_kafka import Producer as KafkaProducer, KafkaError

logger = logging.getLogger(__name__)

stdout = logger.info if DEBUG else print

class Topics:
    tasks_stream = 'tasks-stream'
    tasks = 'tasks'

class Producer:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': 'localhost:9092',
        }
        self.producer = KafkaProducer(self.conf)

    def produce(self, topic, key, value):
        stdout(f'producing to topic `{topic}` with key `{key}` and value {value}')
        self.producer.produce(topic, key=key, value=value, )
