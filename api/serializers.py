from rest_framework import serializers
from .models import Period
from .responses import ERROR_MESSAGES


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ("slug", "name", "start_date", "owner")

    def validate_name(self, value):
        request = self.context.get("request")
        if request.method == "POST":
            if Period.objects.filter(name=value, owner=request.user).exists():
                raise serializers.ValidationError(ERROR_MESSAGES["unique_period_name_per_user"])
        if request.method == "PUT":
            instance = self._args[0]
            if instance.name != value:
                if Period.objects.filter(name=value, owner=request.user).exists():
                    raise serializers.ValidationError(ERROR_MESSAGES["unique_period_name_per_user"])
        return value

    def create(self, validated_data):
        owner = self.context.get("request").user
        return Period.objects.create(**validated_data, owner=owner)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.star_date = validated_data.get("start_date", instance.start_date)
        instance.save()
        return instance


