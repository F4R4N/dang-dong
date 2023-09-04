from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.responses import ERROR_MESSAGES


class MagicLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "is_active", "email")

    def validate_email(self, value):
        user = self.context["request"].user
        if get_user_model().objects.exclude(id=user.id).filter(email=value).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["already_exists"])
        return value

    def validate_username(self, value):
        user = self.context["request"].user
        if get_user_model().objects.exclude(id=user.id).filter(username=value).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["already_exists"])
        return value

    def update(self, instance, validated_data):
        instance.first_name = validated_data.get("first_name", instance.first_name)
        instance.last_name = validated_data.get("last_name", instance.last_name)
        instance.email = validated_data.get("email", instance.email)
        instance.username = validated_data.get("username", instance.username)
        instance.save()
        return instance
