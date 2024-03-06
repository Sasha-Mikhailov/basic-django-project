import logging

logger = logging.getLogger(__name__)


def produce(topic, key, value):
    print(f"producing to topic `{topic}` with key `{key}` and value {value}")
