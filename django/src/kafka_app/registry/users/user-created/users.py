from datetime import datetime
import uuid

from confluent_kafka.serialization import JsonMessageSerializer
from schema_registry.client import schema
from schema_registry.client import SchemaRegistryClient

from app.settings import KAFKA_REGISTRY_HOST

# from confluent_kafka.schema_registry import SchemaRegistryClient


client = SchemaRegistryClient(url=KAFKA_REGISTRY_HOST)

json_schema = schema.JsonSchema(
    {
        "definitions": {
            "users.user-created": {
                "description": "basic schema for users",
                "type": "object",
                "required": [
                    "event_id",
                    "event_version",
                    "event_name",
                    "event_time",
                    "producer",
                    "payload",
                ],
                "properties": {
                    "event_id": {"type": "string"},
                    "event_version": {"type": "int"},
                    "event_name": {"type": "string"},
                    "event_time": {"type": "string"},
                    "producer": {"type": "string"},
                    "payload": {
                        "type": "record",
                        "public_id": {"type": "string"},
                        "username": {"type": "string"},
                        "first_name": {"type": "string"},
                        "last_name": {"type": "string"},
                        "user_role": {"type": "string"},
                    },
                },
            }
        },
        "$ref": "#/definitions/users.user-created",
    }
)

schema_id = client.register(
    subject="users.user-created",
    schema=json_schema,
    schema_type="JSON",
)

test_event = event = {
    "event_id": str(uuid.uuid4()),
    "event_version": "1",
    "event_name": "users.user-created",
    "event_time": datetime.now().isoformat(),
    "producer": "users-service",
    "payload": {
        "public_id": str(uuid.uuid4()),
        "username": str("test-username"),
        "first_name": str("test-first_name"),
        "last_name": str("test-last_name"),
        "user_role": str("WORKER"),
    },
}


json_message_serializer = JsonMessageSerializer(client)

message_encoded = json_message_serializer.encode_record_with_schema("basic", json_schema, test_event)

# this is because the message encoded reserved 5 bytes for the schema_id
assert len(message_encoded) > 5
assert isinstance(message_encoded, bytes)

# Decode the message
message_decoded = json_message_serializer.decode_message(message_encoded)
assert message_decoded == test_event
