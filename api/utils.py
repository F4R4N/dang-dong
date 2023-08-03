import secrets
from django.db.models import Sum
from django.apps import apps


def generate_slug():
    return secrets.token_urlsafe(16)


def purchase_detail_data_generator(person: object, owe_to: list, direct_cost: int, final_cost: int, creditor_of: list):
    return {
        "person": person,
        "owe_to": owe_to,
        "direct_cost": direct_cost,
        "final_cost": final_cost,
        "creditor_of": creditor_of
    }


def purchase_detail_calculator(purchase: object):
    PurchaseMembership = apps.get_model("api", "PurchaseMembership")
    data = []
    purchased_for_users_purchase_membership = PurchaseMembership.objects.filter(purchase=purchase)
    coefficient_sum = purchased_for_users_purchase_membership.aggregate(Sum("coefficient"))["coefficient__sum"]
    each_coefficient_share = purchase.expense / coefficient_sum
    creditor_of = []
    for purchased_for_user in purchased_for_users_purchase_membership.exclude(person=purchase.buyer):
        user_payment_share = each_coefficient_share * purchased_for_user.coefficient
        creditor_of.append({"person": purchased_for_user.person, "amount": user_payment_share})
        data.append(purchase_detail_data_generator(
            person=purchased_for_user.person,
            owe_to=[{
                "person": purchase.buyer,
                "amount": user_payment_share
            }],
            direct_cost=0,
            final_cost=user_payment_share,
            creditor_of=[]
        ))
    buyer_purchase_membership = PurchaseMembership.objects.filter(person=purchase.buyer)
    final_cost = 0
    if buyer_purchase_membership.exists():
        final_cost = each_coefficient_share * buyer_purchase_membership.first().coefficient
    data.append(purchase_detail_data_generator(
        person=purchase.buyer,
        owe_to=[],
        direct_cost=purchase.expense,
        final_cost=final_cost,
        creditor_of=creditor_of
    ))
    return data
