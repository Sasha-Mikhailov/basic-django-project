from rest_framework import serializers

from users.models import User


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

        print(super(user))

        return user

    def update(self, instance, validated_data):
        super().update(instance, validated_data)
        user = User.update_or_create(**instance.data)

        print(super(user))

        return user
