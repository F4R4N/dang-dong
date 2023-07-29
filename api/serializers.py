from rest_framework import serializers, exceptions
from .models import Period, Person, Coefficient, Purchase
from .responses import ERROR_MESSAGES


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("slug", "name", "user", "owner")

    def validate_name(self, value):
        request = self.context["request"]
        if Person.objects.filter(name=value, owner=request.user).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["unique_field"])
        return value

    def create(self, validated_data):
        owner = self.context["request"].user
        return Person.objects.create(**validated_data, owner=owner)


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ("slug", "name", "start_date", "owner", "persons")  # TODO : follow up here

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
    
    def validate_persons(self, value):
        user = self.context["request"].user
        for person in value:
            if person.owner != user:
                raise exceptions.PermissionDenied()

        return value

    def create(self, validated_data):
        owner = self.context.get("request").user
        persons = validated_data.pop("persons")
        period = Period.objects.create(**validated_data, owner=owner)
        period.persons.set(persons)
        return period

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.star_date = validated_data.get("start_date", instance.start_date)
        instance.persons.set(validated_data.get("persons", instance.persons.all()))
        instance.save()
        return instance
    
    def get_related_persons(self, obj):
        print(obj)


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

    def validate(self, attrs):
        persons = attrs["period"].person_set.all()  # all persons tha are related to this period
        if attrs.get("buyer") not in persons:
            raise serializers.ValidationError(ERROR_MESSAGES["not_period_member"])
        for user in attrs.get("purchased_for_users"):
            if user not in persons:
                raise serializers.ValidationError(ERROR_MESSAGES["not_period_member"])
        return attrs

    def create(self, validated_data):
        purchased_for_users = validated_data.pop("purchased_for_users")
        purchase = Purchase.objects.create(**validated_data)
        purchase.purchased_for_users.set(purchased_for_users)
        return purchase
