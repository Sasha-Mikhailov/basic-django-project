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

        p.produce(Topics.users_stream, 'user-created', super(user))
        print(super(user))

        return user

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        user = User.update_or_create(**instance.data)

        p.produce(Topics.users_stream, 'user-updated', super(user))
        print(super(user))

        # TODO add business event with role change

        return user
