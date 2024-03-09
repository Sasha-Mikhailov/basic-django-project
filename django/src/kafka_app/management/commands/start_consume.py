from django.core.management.base import BaseCommand

from kafka_app.consumers.billing_tasks import consume_billing_tasks


class Command(BaseCommand):
    """
    django command

    >>> ./manage.py start_consume
    >>> Waiting for message or event/error in poll()
    """
    help = "Launches Listener for Kafka topic"

    def handle(self, *args, **options):
        consume_billing_tasks()
