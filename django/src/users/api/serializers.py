from datetime import datetime
import uuid

from rest_framework import serializers

from app.settings import Topics
from kafka_app.producer import Producer
from users.models import User

p = Producer()


class UserSerializer(serializers.ModelSerializer):
    remote_addr = serializers.SerializerMethodField()
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "remote_addr",
            "public_id",
            "role",
            "password",
        ]

    def get_remote_addr(self, obj: User) -> str:
        return self.context["request"].META["REMOTE_ADDR"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        event = {
            "event_id": uuid.uuid4(),
            "event_version": 1,
            "event_name": "users.user-created",
            "event_time": datetime.now().isoformat(),
            "producer": "users-service",
            "payload": {
                "public_id": str(user.public_id),
                "username": str(user.username),
                "first_name": str(user.first_name),
                "last_name": str(user.last_name),
                "user_role": str(user.role),
            },
        }
        p.produce(Topics.users_stream, event["event_name"], event)

        return user

    def update(self, instance, validated_data):
        old_role = instance.role
        new_role = validated_data.get("role", old_role)

        super().update(instance, validated_data)
        user = User.update_or_create(**instance.data)

        # TODO think about bulk update
        event = {
            "event_id": uuid.uuid4(),
            "event_version": "1",
            "event_name": "users.user-updated",
            "event_time": datetime.now().isoformat(),
            "producer": "users-service",
            "payload": {
                "public_id": str(user.public_id),
                "username": str(user.username),
                "first_name": str(user.first_name),
                "last_name": str(user.last_name),
                "user_role": str(user.role),
            },
        }
        p.produce(Topics.users_stream, event["event_name"], event)
        # print(validated_data)

        if old_role != new_role:
            event = {
                "event_id": uuid.uuid4(),
                "event_version": "1",
                "event_name": "users.user-role-changed",
                "event_time": datetime.now().isoformat(),
                "producer": "users-service",
                "payload": {
                    "public_id": str(user.public_id),
                    "old_user_role": str(old_role),
                    "new_user_role": str(new_role),
                },
            }
            p.produce(Topics.users, event["event_name"], event)

        return user
