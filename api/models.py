from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from .utils import generate_id


class Person(models.Model):
    id = models.SlugField(verbose_name=_("id"), unique=True, primary_key=True, editable=False, default=generate_id)
    name = models.CharField(verbose_name=_("Name"), max_length=100, blank=False, null=False)
    user = models.ForeignKey(get_user_model(), blank=True, on_delete=models.DO_NOTHING, null=True, verbose_name=_("User"))
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_("Owner"), editable=False, related_name="owner_set")

    def __str__(self):
        return self.name


class Period(models.Model):
    id = models.SlugField(verbose_name=_("id"), unique=True, primary_key=True, max_length=256, editable=False, default=generate_id)
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    start_date = models.DateTimeField(verbose_name=_("Start Date"), default=timezone.now)
    owner = models.ForeignKey(get_user_model(), on_delete=models.CASCADE, verbose_name=_("Owner"), editable=False)
    persons = models.ManyToManyField(Person, verbose_name=_("Person"), blank=True)

    def __str__(self):
        return self.name


class Purchase(models.Model):
    id = models.SlugField(verbose_name=_("id"), unique=True, primary_key=True, editable=False, default=generate_id)
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    date_and_time = models.DateTimeField(default=timezone.now, verbose_name=_("Date and Time"))
    expense = models.PositiveBigIntegerField(verbose_name=_("Expense"))
    buyer = models.ForeignKey(Person, on_delete=models.PROTECT, verbose_name=_("Buyer"), related_name="purchase_set_buyer")
    period = models.ForeignKey(Period, on_delete=models.CASCADE, verbose_name=_("Period"))

    def __str__(self):
        return self.name


class PurchaseMembership(models.Model):
    id = models.SlugField(verbose_name=_("id"), unique=True, primary_key=True, editable=False, default=generate_id)
    coefficient = models.IntegerField(verbose_name=_("Coefficient"), default=1, validators=[MinValueValidator(1)])
    person = models.ForeignKey(Person, on_delete=models.PROTECT)
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="purchased_for_users")

    def __str__(self) -> str:
        return str(self.coefficient)

# NOTE: TODO: REMEMBER TO CHECK PERSON DELETION AND WHAT HAPPENS TO THE OBJECTS RELATED.
