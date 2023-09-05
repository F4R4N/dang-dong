from django.contrib.auth import get_user_model
from rest_framework import serializers

from api.responses import ERROR_MESSAGES


class MagicLinkSerializer(serializers.Serializer):
    """use to verify user email input against email field format and being required."""

    email = serializers.EmailField(required=True)


class UserSerializer(serializers.ModelSerializer):
    """
    UserSerializer is a Django Rest Framework serializer class used to validate and update user data.

    It contains the Meta class with model set to :model:`customauth.User` and fields set to id, username, first_name, last_name, is_active, and email.

    The validate_email and validate_username methods are used to check if the email or username already exists in the database.
    If it does, an error message is raised.

    The update method is used to update the instance of the user with the new validated data from user.
    """

    class Meta:
        model = get_user_model()
        fields = ("id", "username", "first_name", "last_name", "is_active", "email")

    def validate_email(self, value):
        """
        check if given email address does exists in DB.

        Args:
            self (object): The serializer object.
            value (str): The email address to be validated.

        Returns:
            str: The email address if valid.

        Raises:
            serializers.ValidationError: If the email address already exists.
        """
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
