from django.contrib import admin
from .models import Period, Person, Purchase


@admin.register(Person)
class PersonAdmin(admin.ModelAdmin):
	list_display = ("name", "user", "period", "coefficient")


@admin.register(Period)
class PeriodAdmin(admin.ModelAdmin):
	list_display = ("name", "start_date", "owner")


@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
	list_display = ("name", "date_and_time", "expense", "buyer", "get_purchase_users", "period")
	
	def get_purchase_users(self, instance):
		result = []
		for person in instance.purchase_users.all():
			result.append(person.name)
		return result