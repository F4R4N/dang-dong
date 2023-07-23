from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from .utils import generate_slug


class Period(models.Model):
    slug = models.SlugField(verbose_name=_("Slug"), unique=True, primary_key=True, max_length=256, editable=False, default=generate_slug)
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    start_date = models.DateTimeField(verbose_name=_("Start Date"), default=timezone.now)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_("Owner"), editable=False)

    def __str__(self):
        return self.name
# TODO: add a method to calculate all expenses


class Person(models.Model):
    slug = models.SlugField(verbose_name=_("Slug"), unique=True, primary_key=True, editable=False, default=generate_slug)
    name = models.CharField(verbose_name=_("Name"), max_length=100, blank=False, null=False)
    user = models.ForeignKey(get_user_model(), blank=True, on_delete=models.DO_NOTHING, null=True, verbose_name=_("User"))
    period = models.ForeignKey(Period, on_delete=models.DO_NOTHING, verbose_name=_("Period"), null=False, blank=False)

    def __str__(self):
        return self.name
# TODO: check user name uniqueness in serializers based on users in "period"


class Purchase(models.Model):
    slug = models.SlugField(verbose_name=_("Slug"), unique=True, primary_key=True, editable=False, default=generate_slug)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    date_and_time = models.DateTimeField(default=timezone.now, verbose_name=_("Date and Time"))
    expense = models.PositiveBigIntegerField(verbose_name=_("Expense"))
    buyer = models.ForeignKey(Person, on_delete=models.PROTECT, verbose_name=_("Buyer"), related_name="purchase_set_buyer")
    purchased_for_users = models.ManyToManyField(Person, verbose_name=_("Purchased For Users"))
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name=_("Period"))

    def __str__(self):
        return self.name
# NOTE: get owner of purchase and person with reverse access to period owner


# NOTE EVERY PERSON PER PURCHASE CAN HAVE ONLY ONE COEFFICIENT !!!!!
class Coefficient(models.Model):
    slug = models.SlugField(verbose_name=_("Slug"), unique=True, primary_key=True, editable=False, default=generate_slug)
    coefficient = models.IntegerField(verbose_name=_("Coefficient"), default=1, validators=[MinValueValidator(1)])
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, on_delete=models.CASCADE)

    def __str__(self) -> str:
        return self.coefficient
