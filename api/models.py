from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator


class Period(models.Model):
    name = models.CharField(max_length=100)
    start_date = models.DateField(default=timezone.now)
    owner = models.OneToOneField(get_user_model(), on_delete=models.CASCADE)

    def __str__(self):
        return self.name
# TODO: check period name uniqueness in serializers based on owners period
# TODO: add a method to calculate all expences


class Person(models.Model):
    name = models.CharField(max_length=100)
    user = models.ForeignKey(get_user_model(), blank=True, on_delete=models.DO_NOTHING, null=True)
    periods = models.ForeignKey(Period, on_delete=models.DO_NOTHING)
    coefficient = models.IntegerField(default=1, validators=[MinValueValidator(1)])

    def __str__(self):
        return self.name
# TODO: check user name uniqueness in serializers based on users in period


class Purchase(models.Model):
    name = models.CharField(max_length=100)
    date_and_time = models.DateTimeField(default=timezone.now)
    expense = models.PositiveBigIntegerField()
    buyer = models.ForeignKey(Person, on_delete=models.PROTECT)
    purchase_users = models.ManyToManyField(Person)
    period = models.ForeignKey(Period, on_delete=models.CASCADE)

    def __str__(self):
        return self.name
# NOTE: get owner of purchase and person with reverse access to period owner
