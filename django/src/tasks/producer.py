import logging

from confluent_kafka import Producer as KafkaProducer, KafkaError

from app.settings import DEBUG, KAFKA_HOST

logger = logging.getLogger(__name__)

stdout = print if DEBUG else logger.info


class Producer:
    def __init__(self):
        self.conf = {
            'bootstrap.servers': KAFKA_HOST,
        }
        self.producer = KafkaProducer(self.conf)

    def produce(self, topic, key, value):
        stdout(f'producing to topic `{topic}` with key `{key}` and value {value}')
        self.producer.produce(topic, key=key, value=value, )
