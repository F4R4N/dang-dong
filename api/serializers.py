from rest_framework import serializers, exceptions
from .models import Period, Person
from .responses import ERROR_MESSAGES


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ("slug", "name", "start_date", "owner")

    def validate_name(self, value):
        request = self.context.get("request")
        if request.method == "POST":
            if Period.objects.filter(name=value, owner=request.user).exists():
                raise serializers.ValidationError(ERROR_MESSAGES["unique_field"])
        if request.method == "PUT":
            instance = self._args[0]
            if instance.name != value:
                if Period.objects.filter(name=value, owner=request.user).exists():
                    raise serializers.ValidationError(ERROR_MESSAGES["unique_field"])
        return value

    def create(self, validated_data):
        owner = self.context.get("request").user
        return Period.objects.create(**validated_data, owner=owner)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.star_date = validated_data.get("start_date", instance.start_date)
        instance.save()
        return instance


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("slug", "name", "user", "period", "coefficient")

    def validate_period(self, value):
        request = self.context["request"]
        if request.method == "POST":
            if value.owner != request.user:
                raise exceptions.PermissionDenied()
        return value

    def validate(self, attrs):
        if Person.objects.filter(name=attrs.get("name"), period=attrs.get("period")).exists():
            raise serializers.ValidationError({"name": ERROR_MESSAGES["unique_field"]})
        return attrs

    def create(self, validated_data):
        return Person.objects.create(**validated_data)
