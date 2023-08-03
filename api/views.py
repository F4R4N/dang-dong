from rest_framework import viewsets, status
from .serializers import PeriodSerializer, PersonSerializer, PurchaseSerializer, PurchaseSerializerForRead, PurchaseMembership, CustomPurchaseDetailSerializer
from .models import Period, Person, Purchase
from rest_framework.response import Response
from rest_framework.generics import RetrieveAPIView
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner
from django.db.models import Sum
from .responses import RESPONSE_MESSAGES, ERROR_MESSAGES
from django.shortcuts import get_object_or_404


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PeriodSerializer
    http_method_names = ["get", "post", "delete", "put"]

    def perform_create(self, serializer):
        serializer.save()

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, pk=None):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT, data={"detail": RESPONSE_MESSAGES["successfully_deleted"]})

    def list(self, request):
        periods = Period.objects.filter(owner=request.user)
        serializer = self.get_serializer(periods, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def retrieve(self, request, pk=None):
        instance = get_object_or_404(Period, pk=pk)
        period_serializer = PeriodSerializer(instance)
        purchase_serializer = PurchaseSerializerForRead(instance.purchase_set.all(), many=True)
        return Response(status=status.HTTP_200_OK, data={"period": period_serializer.data, "all_purchases": purchase_serializer.data})


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PersonSerializer
    http_method_names = ["get", "post", "delete"]

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, pk=None):
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        return Response(status=status.HTTP_204_NO_CONTENT, data={RESPONSE_MESSAGES["successfully_deleted"]})

    def list(self, request):
        persons = Person.objects.filter(owner=request.user)
        serializer = self.get_serializer(persons, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = PurchaseSerializer
    http_method_names = ["post", "get", "delete", "put"]

    def perform_create(self, serializer):
        serializer.save()

    def list(self, request):
        if "period" not in request.data:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={"period": ERROR_MESSAGES["required_field"]})
        period = get_object_or_404(Period, slug=request.data["period"])
        if period.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data=ERROR_MESSAGES["permission_denied"])
        purchases = Purchase.objects.filter(period=period)
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, pk=None):
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        return Response(status=status.HTTP_204_NO_CONTENT, data={RESPONSE_MESSAGES["successfully_deleted"]})

    # NOTE: REMEMBER TO ADD RETRIEVE FOR DETAIL SHIT IN A PURCHASE


class PurchaseExpenseDetail(APIView):
    permission_classes = (IsAuthenticated,)
    # http_method_names = ["get"]

    def get(self, request, pk, format=None):
        purchase = get_object_or_404(Purchase, pk=pk)
        if purchase.period.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN, data={"detail": ERROR_MESSAGES["permission_denied"]})
        purchased_for_users = PurchaseMembership.objects.filter(purchase=purchase)
        coefficient_sum = purchased_for_users.aggregate(Sum("coefficient"))["coefficient__sum"]
        each_coefficient_share = purchase.expense / coefficient_sum
        data = []
        creditor_of = []
        for purchased_for_user in purchased_for_users:
            if purchased_for_user.person != purchase.buyer:
                creditor_of.append({"person": purchased_for_user.person, "amount": each_coefficient_share * purchased_for_user.coefficient})
            if purchased_for_user.person == purchase.buyer:
                final_cost = 0
                buyer_purchase_membership = purchased_for_users.filter(person=purchase.buyer)
                if buyer_purchase_membership.exists():

                    final_cost = each_coefficient_share * buyer_purchase_membership.first().coefficient
                data.append({
                    "person": purchase.buyer,
                    "owe_to": [],
                    "direct_cost": purchase.expense,
                    "final_cost": final_cost,
                    "creditor_of": creditor_of
                })

            else:
                data.append({
                    "person": purchased_for_user.person,
                    "owe_to": [{"person": purchase.buyer, "amount": each_coefficient_share * purchased_for_user.coefficient}],
                    "direct_cost": 0,
                    "final_cost": each_coefficient_share * purchased_for_user.coefficient,
                    "creditor_of": []
                })
        serializer = CustomPurchaseDetailSerializer(data, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)
# TODO: TRY TO CLEAN THIS AND BREAK IT TO MULTIPLE FUNCTIONS. AND TRY TO USE SERIALIZERS AND VIEWSETS INSTEAD