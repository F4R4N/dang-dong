from rest_framework import serializers, exceptions
from .models import Period, Person, Purchase, PurchaseMembership
from .responses import ERROR_MESSAGES


class PersonSerializer(serializers.ModelSerializer):
    class Meta:
        model = Person
        fields = ("id", "name", "user", "owner")

    def validate_name(self, value):
        request = self.context["request"]
        if Person.objects.filter(name=value, owner=request.user).exists():
            raise serializers.ValidationError(ERROR_MESSAGES["unique_field"])
        return value

    def create(self, validated_data):
        owner = self.context["request"].user
        return Person.objects.create(**validated_data, owner=owner)


class PurchaseSerializerForRead(serializers.ModelSerializer):
    buyer = PersonSerializer()

    class Meta:
        model = Purchase
        fields = ("id", "buyer", "name", "expense", "date_and_time")


class PeriodSerializer(serializers.ModelSerializer):
    class Meta:
        model = Period
        fields = ("id", "name", "start_date", "owner", "persons")

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
        persons = validated_data.get("persons", instance.persons.all())
        persons_in_purchases: set[object] = set()
        for periods_purchase in instance.purchase_set.all():
            for purchase_membership in periods_purchase.purchased_for_users.all():
                persons_in_purchases.add(purchase_membership.person)
            persons_in_purchases.add(periods_purchase.buyer)
        if not persons_in_purchases.issubset(set(persons)):
            raise serializers.ValidationError({"persons": ERROR_MESSAGES["person_object_protected"]})
        instance.persons.set(persons)
        instance.save()
        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        person_serializer = PersonSerializer(instance.persons.all(), many=True)
        representation["persons"] = person_serializer.data
        return representation


class PurchaseMemberShipSerializer(serializers.ModelSerializer):
    class Meta:
        model = PurchaseMembership
        fields = ("id", "coefficient", "person")


class PurchaseMemberShipSerializerForRead(serializers.ModelSerializer):
    person = PersonSerializer(read_only=True)

    class Meta:
        model = PurchaseMembership
        fields = ("coefficient", "person")


class PurchaseSerializer(serializers.ModelSerializer):
    purchased_for_users = PurchaseMemberShipSerializer(many=True, required=True)

    class Meta:
        model = Purchase
        fields = ("id", "name", "date_and_time", "expense", "buyer", "purchased_for_users", "period")

    def validate_name(self, value):
        request = self.context.get("request")
        if request.method == "POST":
            if Purchase.objects.filter(name=value, period__owner=request.user).exists():
                raise serializers.ValidationError(ERROR_MESSAGES["unique_field"])
        if request.method == "PUT":
            instance = self._args[0]
            if instance.name != value:
                if Period.objects.filter(name=value, owner=request.user).exists():
                    raise serializers.ValidationError(ERROR_MESSAGES["unique_field"])
        return value

    def validate_buyer(self, value):
        request = self.context["request"]
        if value.owner != request.user:
            raise exceptions.PermissionDenied()
        return value

    def validate_purchased_for_users(self, value):
        request = self.context["request"]
        for person_data in value:
            if person_data.get("person").owner != request.user:
                raise exceptions.PermissionDenied()
        return value

    def validate_period(self, value):
        request = self.context["request"]
        if value.owner != request.user:
            raise exceptions.PermissionDenied()
        return value

    def validate(self, attrs):
        persons = attrs["period"].persons.all()  # all persons tha are related to this period
        if attrs.get("buyer") not in persons:
            raise serializers.ValidationError({"buyer": ERROR_MESSAGES["not_period_member"]})
        for user_data in attrs.get("purchased_for_users"):
            if user_data.get("person") not in persons:
                raise serializers.ValidationError(ERROR_MESSAGES["not_period_member"])
        return attrs

    def create(self, validated_data):
        purchased_for_users = validated_data.pop("purchased_for_users")
        purchase = Purchase.objects.create(**validated_data)
        for person_data in purchased_for_users:
            membership = PurchaseMembership(
                coefficient=person_data.get("coefficient"),
                purchase=purchase,
                person=person_data.get("person")
            )
            membership.save()
        return purchase

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        buyer_serializer = PersonSerializer(instance.buyer)
        period_serializer = PeriodSerializer(instance.period)
        purchased_for_users_serializer = PurchaseMemberShipSerializerForRead(instance.purchased_for_users.all(), many=True)
        representation["buyer"] = buyer_serializer.data
        representation["period"] = period_serializer.data
        representation["purchased_for_users"] = purchased_for_users_serializer.data

        return representation

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.date_and_time = validated_data.get("date_and_time", instance.date_and_time)
        instance.expense = validated_data.get("expense", instance.expense)
        instance.buyer = validated_data.get("buyer", instance.buyer)
        for user_data in validated_data.get("purchased_for_users"):
            try:
                purchase_membership = PurchaseMembership.objects.get(purchase=instance, person=user_data.get("person"))
                purchase_membership.coefficient = user_data.get("coefficient")
                purchase_membership.save()
            except PurchaseMembership.DoesNotExist:
                purchase_membership = PurchaseMembership.objects.create(
                    coefficient=user_data.get("coefficient"),
                    person=user_data.get("person"),
                    purchase=instance
                )
        instance.save()
        return instance


class InDebtAndCreditedSerializer(serializers.Serializer):
    person = PersonSerializer()
    amount = serializers.IntegerField()


class DetailSerializer(serializers.Serializer):
    person = PersonSerializer()
    owe_to = InDebtAndCreditedSerializer(many=True)
    direct_cost = serializers.IntegerField()
    final_cost = serializers.IntegerField()
    creditor_of = InDebtAndCreditedSerializer(many=True)
