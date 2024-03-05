import uuid

from rest_framework import serializers

from app.settings import Topics

from users.models import User
from tasks.producer import Producer


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
            # TODO add version, name, time, producer
            "payload": {
                "public_id": str(user.public_id),
                "username": str(user.username),
                "user_role": str(user.role),
            },
        }
        p.produce(Topics.users_stream, 'users.user-created', event)

        return user

    def update(self, instance, validated_data):
        old_role = instance.role
        new_role = validated_data.get('role', old_role)

        super().update(instance, validated_data)
        user = User.update_or_create(**instance.data)

        # TODO think about bulk update
        event = {
            "event_id": uuid.uuid4(),
            # TODO add version, name, time, producer
            "payload": {
                "public_id": str(user.public_id),
                "username": str(user.username),
                "user_role": str(user.role),
            },
        }
        p.produce(Topics.users_stream, 'users.user-updated', event)
        # print(validated_data)

        if old_role != new_role:
            event = {
                "event_id": uuid.uuid4(),
                # TODO add version, name, time, producer
                "payload": {
                    "public_id": str(user.public_id),
                    "old_user_role": str(old_role),
                    "new_user_role": str(new_role),
                },
            }
            p.produce(Topics.users, 'users.user-role-changed', instance.data)

        return user
