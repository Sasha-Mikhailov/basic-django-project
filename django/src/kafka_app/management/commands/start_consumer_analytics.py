from django.core.management.base import BaseCommand

from kafka_app.consumers.analytics import start_analytics_consumer


class Command(BaseCommand):
    """
    django command

    >>> ./manage.py start_consumer_analytics
    """

    help = "Launches Listener for Kafka topic"

    def handle(self, *args, **options):
        start_analytics_consumer()
