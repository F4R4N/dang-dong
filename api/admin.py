from django.contrib import admin
from .models import Period, Person, Purchase


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
	list_display = ("name", "user", "owner",)


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
	list_display = ("name", "slug", "start_date", "owner", "get_persons")

	def get_persons(self, instance):
		result = []
		for person in instance.persons.all():
			result.append(person.name)
		return result


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
	list_display = ("name", "date_and_time", "expense", "buyer", "get_purchase_users", "period")
	
	def get_purchase_users(self, instance):
		result = []
		for person in instance.purchased_for_users.all():
			result.append(person.name)
		return result
