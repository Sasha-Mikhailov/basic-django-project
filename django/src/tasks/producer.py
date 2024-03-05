import logging

from confluent_kafka import Producer as KafkaProducer, KafkaError

from app.settings import DEBUG, KAFKA_HOST, KAFKA_DRY_RUN

logger = logging.getLogger(__name__)

stdout = print if DEBUG else logger.info


class Producer:
    def __init__(self, conf: dict=None, dry_run: bool=None):
        self.conf = {
            'bootstrap.servers': KAFKA_HOST,
        }
        self.dry_run = dry_run or KAFKA_DRY_RUN

        if not self.dry_run:
            self.producer = KafkaProducer(self.conf)

    def produce(self, topic, key, value):
        stdout(f'producing to topic `{topic}` with key `{key}` and value {value}')
        if not self.dry_run:
            self.producer.produce(topic, key=key, value=value, )
