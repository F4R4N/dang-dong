from rest_framework import serializers, exceptions
from .models import Period, Person, Coefficient, Purchase
from .responses import ERROR_MESSAGES
from django.core.validators import MinValueValidator


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


class PurchaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purchase
        fields = ("slug", "name", "date_and_time", "expense", "buyer", "purchased_for_users", "period")

    def validate_buyer(self, value):
        request = self.context["request"]
        if value.period.owner != request.user:
            raise exceptions.PermissionDenied()
        return value

    def validate_period(self, value):
        request = self.context["request"]
        if value.owner != request.user:
            raise exceptions.PermissionDenied()
        return value

    def validate_purchased_for_users(self, value):
        request = self.context["request"]
        for person in value:
            if person.period.owner != request.user:
                raise exceptions.PermissionDenied()
        return value

    def create(self, validated_data):
        purchased_for_users = validated_data.pop("purchased_for_users")
        purchase = Purchase.objects.create(**validated_data)
        purchase.purchased_for_users.set(purchased_for_users)
        return purchase
    


class PersonSerializer(serializers.ModelSerializer):
    coefficient = serializers.IntegerField(validators=[MinValueValidator(1)], required=True)

    class Meta:
        model = Person
        fields = ("slug", "name", "user", "period", "coefficient")

    def validate_period(self, value):
        request = self.context["request"]
        if request.method in ["POST", "PUT"]:
            if value.owner != request.user:
                raise exceptions.PermissionDenied()
        return value

    def validate(self, attrs):
        request = self.context["request"]
        if Person.objects.filter(name=attrs.get("name"), user=request.user).exists():
            raise serializers.ValidationError({"name": ERROR_MESSAGES["unique_field"]})
        return attrs

    def create(self, validated_data):
        return Person.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.coefficient = validated_data.get("name", instance.coefficient)
        instance.save()
        return instance
