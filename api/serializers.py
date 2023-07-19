from rest_framework import serializers
from .models import Period
from .errors import ERROR_MESSAGES


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ("slug", "name", "start_date", "owner")

    def validate_name(self, value):
        user = self.context.get("request").user
        if Period.objects.filter(name=value, owner=user).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["unique_period_name_per_user"])
        return value

    def create(self, validated_data):
        owner = self.context.get("request").user
        return Period.objects.create(**validated_data, owner=owner)

