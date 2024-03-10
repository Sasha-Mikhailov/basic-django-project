from django.core.management.base import BaseCommand

from kafka_app.consumers.billing import start_billing_consumer


class Command(BaseCommand):
    """
    django command

    >>> ./manage.py start_consume__billing_tasks
    """

    help = "Launches Listener for Kafka topic"

    def handle(self, *args, **options):
        start_billing_consumer()
