from rest_framework import serializers
from django.contrib.auth import get_user_model


class MagicLinkSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "is_active", "email")

    # def update(self, instance, validated_data):
    #     return super().update(instance, validated_data)