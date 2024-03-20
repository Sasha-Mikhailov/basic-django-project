from typing import Any

from behaviors.behaviors import Timestamped  # type: ignore

from django.contrib.contenttypes.models import ContentType
from django.db import models

__all__ = [
    "models",
    "DefaultModel",
    "TimestampedModel",
]


class DefaultModel(models.Model):
    class Meta:
        abstract = True

    def __str__(self) -> str:
        """Default name for all models"""
        public_id = getattr(self, "public_id", None)
        if public_id is not None:
            return str(public_id)

        name = getattr(self, "name", None)
        if name is not None:
            return str(name)

        return super().__str__()

    @classmethod
    def get_contenttype(cls) -> ContentType:
        return ContentType.objects.get_for_model(cls)

    def update_from_kwargs(self, **kwargs: dict[str, Any]) -> None:
        """A shortcut method to update model instance from the kwargs."""
        for key, value in kwargs.items():
            setattr(self, key, value)

    def setattr_and_save(self, key: str, value: Any) -> None:
        """Shortcut for testing -- set attribute of the model and save"""
        setattr(self, key, value)
        self.save()

    @classmethod
    def get_label(cls) -> str:
        """Get a unique within the app model label"""
        return cls._meta.label_lower.split(".")[-1]


class TimestampedModel(DefaultModel, Timestamped):
    """
    Default app model that has `created` and `updated` attributes.
    Currently based on https://github.com/audiolion/django-behaviors
    """

    class Meta:
        abstract = True


class EventLogModel(DefaultModel, Timestamped):
    """
    default model for event logs to keep every event in the system no matter the payload schema
    """

    class Meta:
        abstract = True

    # keep the event meta to scan events in db
    event_id = models.UUIDField(blank=False, null=False)
    event_version = models.TextField(null=True)
    event_name = models.TextField(null=True)
    producer = models.TextField(null=True)

    # dump the whole payload as json string no matter the schema
    payload = models.JSONField()
