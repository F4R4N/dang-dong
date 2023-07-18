from django.contrib import admin
from .models import Period, Person


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
	list_display = ("name", "user", "periods", "coefficient")


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
	list_display = ("name", "start_date", "owner")
