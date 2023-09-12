from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from .codes import generate_id, generate_period_sharing_id


class Person(models.Model):
    """
    This model represents a Person. It contains fields for the person's id, name, user, and owner (user that own that is authorized
    to add that person to its periods and purchases).
    Attributes:
        id (SlugField): Unique identifier for the person.
        name (CharField): Name of the person.
        user (ForeignKey): :model:`customauth.User` associated with the person.
        owner (ForeignKey): :model:`customauth.User` that owns of the person.
    """

    id = models.SlugField(
        verbose_name=_("Id"),
        unique=True,
        primary_key=True,
        editable=False,
        default=generate_id,
    )
    name = models.CharField(
        verbose_name=_("Name"), max_length=100, blank=False, null=False
    )
    user = models.ForeignKey(
        get_user_model(),
        blank=True,
        on_delete=models.DO_NOTHING,
        null=True,
        verbose_name=_("User"),
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
        editable=False,
        related_name="owner_set",
    )

    def __str__(self):
        return self.name


class Period(models.Model):
    """
    This model represents a period of time which the purchased happens in, with a name, start date, owner and persons associated with it.
    Attributes:
        id (SlugField): A unique identifier for the period.
        name (CharField): The name of the period.
        start_date (DateTimeField): The start date of the period.
        owner (ForeignKey): The :model:`customauth.User` who owns the period.
        persons (ManyToManyField): :model:`api.Person` associated with the period.
    """

    id = models.SlugField(
        verbose_name=_("Id"),
        unique=True,
        primary_key=True,
        max_length=256,
        editable=False,
        default=generate_id,
    )
    name = models.CharField(verbose_name=_("Name"), max_length=100)
    start_date = models.DateTimeField(
        verbose_name=_("Start Date"), default=timezone.now
    )
    owner = models.ForeignKey(
        get_user_model(),
        on_delete=models.CASCADE,
        verbose_name=_("Owner"),
        editable=False,
    )
    persons = models.ManyToManyField(Person, verbose_name=_("Person"), blank=True)

    def __str__(self):
        return self.name


class PeriodShare(models.Model):
    id = models.SlugField(
        verbose_name=_("Id"),
        unique=True,
        primary_key=True,
        max_length=256,
        editable=False,
        default=generate_id,
    )
    period = models.ForeignKey(
        Period,
        on_delete=models.CASCADE,
        verbose_name=_("Period"),
    )
    sharing_id = models.CharField(
        unique=True,
        default=generate_period_sharing_id,
        verbose_name=_("Sharing Id"),
        editable=False,
        max_length=256,
    )
    expires_at = models.DateTimeField(verbose_name=_("Expires At"))

    def __str__(self) -> str:
        return str(self.period.name)

    def is_expired(self) -> bool:
        return self.expires_at < timezone.now()


class Purchase(models.Model):
    """
    This model represents a Purchase. It contains information about the purchase such as its name, date and time, expense, buyer, and period.
    Attributes:
        id (SlugField): Unique identifier for the purchase.
        name (CharField): Name of the purchase.
        date_and_time (DateTimeField): Date and time when the purchase was made.
        expense (PositiveBigIntegerField): Amount spent on the purchase.
        buyer (ForeignKey): :model:`api.Person` who made the purchase.
        period (ForeignKey): :model:`api.Period` in which the purchase was made.
    """

    id = models.SlugField(
        verbose_name=_("id"),
        unique=True,
        primary_key=True,
        editable=False,
        default=generate_id,
    )
    name = models.CharField(max_length=100, verbose_name=_("Name"))
    date_and_time = models.DateTimeField(
        default=timezone.now, verbose_name=_("Date and Time")
    )
    expense = models.PositiveBigIntegerField(verbose_name=_("Expense"))
    buyer = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_("Buyer"),
        related_name="purchase_set_buyer",
    )
    period = models.ForeignKey(
        Period, on_delete=models.CASCADE, verbose_name=_("Period")
    )

    def __str__(self):
        return self.name


class PurchaseMembership(models.Model):
    """
    This model represents a PurchaseMembership, which is used to store information about a person's each purchase in each period.
    Attributes:
        id (SlugField): A unique identifier for the membership.
        coefficient (IntegerField): The coefficient of the person membership in this purchase.
        person (ForeignKey): The :model:`api.Person` associated with the membership.
        purchase (ForeignKey): The :model:`api.Purchase` associated with the membership.
    """

    id = models.SlugField(
        verbose_name=_("id"),
        unique=True,
        primary_key=True,
        editable=False,
        default=generate_id,
    )
    coefficient = models.IntegerField(
        verbose_name=_("Coefficient"), default=1, blank=True, null=True, validators=[MinValueValidator(1)]
    )
    person = models.ForeignKey(
        Person,
        on_delete=models.CASCADE,
        verbose_name=_("Person"),
    )
    purchase = models.ForeignKey(
        Purchase,
        on_delete=models.CASCADE,
        related_name="purchased_for_users",
        verbose_name=_("Purchase"),
    )
    # direct_cost = models.PositiveBigIntegerField(default=0)
    # final_cost = models.PositiveBigIntegerField(default=0)

    def __str__(self) -> str:
        return str(self.coefficient)


# class OweAndCredit(models.Model):
#     CHOICES = (
#         ("owe_to", "Owe To"),
#         ("creditor_of", "Creditor Of")
#     )
#     detail = models.ForeignKey(PurchaseMembership, on_delete=models.CASCADE)
#     types = models.CharField(max_length=20, choices=CHOICES)
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     amount = models.PositiveBigIntegerField()

#     def __str__(self):
#         return str(self.person.name)
