import secrets
from django.db.models import Sum  # type: ignore
from django.apps import apps  # type: ignore
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .models import Purchase


def generate_id() -> str:
    """ generates a url-safe token to use as id in models. """
    return secrets.token_urlsafe(16)


def purchase_detail_data_generator(person: object, owe_to: list, direct_cost: int, final_cost: int, creditor_of: list) -> dict:
    """
    generates purchase detail data in a certain format.
    Args:
        person (object): The person making the purchase.
        owe_to (list): A list of people the purchaser owes money to.
        direct_cost (int): The cost of the purchase before any additional fees.
        final_cost (int): The total cost of the purchase after all fees and taxes.
        creditor_of (list): A list of people the purchaser is a creditor of.

    Returns:
        dict: A dictionary containing details of the purchase.
    """
    return {
        "person": person,
        "owe_to": owe_to,
        "direct_cost": direct_cost,
        "final_cost": final_cost,
        "creditor_of": creditor_of
    }


def purchase_detail_calculator(purchase: 'Purchase') -> list:
    """
    Calculates the purchase details for a given purchase.

    Args:
        purchase (Purchase): The purchase to calculate the details for.

    Returns:
        list: A list of purchase detail data objects.
            format:
                "person": person,
                "owe_to": owe_to,
                "direct_cost": direct_cost,
                "final_cost": final_cost,
                "creditor_of": creditor_of
    """
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
    buyer_purchase_membership = PurchaseMembership.objects.filter(person=purchase.buyer, purchase=purchase)
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


def get_dict_index(lst: list, key: str, value: object) -> int:
    """
    Returns the index of the dictionary in the given list which contains the given key-value pair.

    Args:
        lst (list): The list of dictionaries to search through.
        key (str): The key to search for in the dictionaries.
        value (object): The value associated with the given key.

    Returns:
        int: The index of the dictionary containing the given key-value pair, or -1 if not found.
    """
    for index, dic in enumerate(lst):
        if dic[key] == value:
            return index
    return -1


def owe_and_credit_calculator(owe_or_credits: list[dict[str, object | int]]) -> list[dict[str, object | int]]:
    """Calculates the total amount owed or credited by each person in a given list of transactions.

    Args:
        owe_or_credits (list[dict[str, object | int]]): A list of dictionaries containing information about each transaction.
        Each dictionary should contain two keys: "person" and "amount".

    Returns:
        list[dict[str, object | int]]: A list of dictionaries containing the total amount owed or credited by each person.
        Each dictionary contains two keys: "person" and "amount".
    """
    data: list[dict[str, object | int]] = []
    for owe_or_credit in owe_or_credits:
        if any(element["person"] == owe_or_credit["person"] for element in data):
            index: int = get_dict_index(data, "person", owe_or_credit["person"])
            data[index].update({"amount": data[index]["amount"] + owe_or_credit["amount"]})
        else:
            data.append(owe_or_credit)
    return data
