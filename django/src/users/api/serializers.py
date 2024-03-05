from rest_framework import serializers

from app.settings import Topics

from users.models import User
from tasks.producer import Producer


p = Producer()

class UserSerializer(serializers.ModelSerializer):
    remote_addr = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "remote_addr",
        ]

    def get_remote_addr(self, obj: User) -> str:
        return self.context["request"].META["REMOTE_ADDR"]

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)

        p.produce(Topics.users_stream, 'users.user-created', super(user))
        print(super(user))

        return user

    def update(self, instance, validated_data):
        old_role = instance.role
        new_role = validated_data.get('role', old_role)

        super().update(instance, validated_data)
        user = User.update_or_create(**instance.data)

        # TODO think about bulk update
        # TODO add meta and payload
        p.produce(Topics.users_stream, 'users.user-updated', super(user))
        print(super(user))

        if old_role != new_role:
            p.produce(Topics.users, 'users.user-role-changed', super(user))

        return user
