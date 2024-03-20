from django.core.management.base import BaseCommand

from kafka_app.consumers.tasks import start_consumer_tasks


class Command(BaseCommand):
    """
    django command

    >>> ./manage.py start_consume__tasks_users
    """

    help = "Launches Listener for Kafka topic"

    def handle(self, *args, **options):
        start_consumer_tasks()
