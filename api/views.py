from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Period, Person, Purchase
from .permissions import IsOwner, IsPurchaseOwner
from .responses import ERROR_MESSAGES, RESPONSE_MESSAGES
from .serializers import (DetailSerializer, PeriodSerializer, PersonSerializer,
                          PurchaseSerializer, PurchaseSerializerForRead)
from .utils import (get_dict_index, owe_and_credit_calculator,
                    purchase_detail_calculator)


class PeriodViewSet(viewsets.ModelViewSet):
    """perform create, update, destroy, list, retrieve actions on period object"""

    queryset = Period.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PeriodSerializer
    http_method_names = ["get", "post", "delete", "put"]

    def perform_create(self, serializer):
        """creates a new period with the given data"""
        serializer.save()

    def perform_update(self, serializer):
        """update the already existing period with the given data"""
        serializer.save()

    def destroy(self, request, pk=None):
        """delete the period with the given id"""
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={"detail": RESPONSE_MESSAGES["successfully_deleted"]},
        )

    def list(self, request: Request) -> Response:
        """list all periods of user"""
        periods = Period.objects.filter(owner=request.user)  # type: ignore
        serializer = self.get_serializer(periods, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def retrieve(self, request, pk=None):
        """return detailed data about the period with the given id. including period info, purchases info and expenses detail."""
        period = get_object_or_404(Period, pk=pk)
        all_periods_purchases = period.purchase_set.all()
        period_detail: list[dict[str, object | int | dict[str, int | object]]] = []
        for purchase in all_periods_purchases:
            purchase_detail_calculator_result = purchase_detail_calculator(
                purchase=purchase
            )
            for person_detail in purchase_detail_calculator_result:
                if any(
                    element["person"] == person_detail["person"]
                    for element in period_detail
                ):  # True when person exist in period_detail (update())
                    index = get_dict_index(
                        period_detail, "person", person_detail["person"]
                    )
                    period_detail[index].update(
                        {
                            "direct_cost": period_detail[index]["direct_cost"]
                            + person_detail["direct_cost"],
                            "final_cost": period_detail[index]["final_cost"]
                            + person_detail["final_cost"],
                            "owe_to": period_detail[index]["owe_to"]
                            + person_detail["owe_to"],
                            "creditor_of": period_detail[index]["creditor_of"]
                            + person_detail["creditor_of"],
                        }
                    )
                else:
                    period_detail.append(person_detail)
        for detail in period_detail:
            owe_tos = owe_and_credit_calculator(detail["owe_to"])
            creditor_ofs = owe_and_credit_calculator(detail["creditor_of"])
            period_detail[period_detail.index(detail)].update({"owe_to": owe_tos})
            period_detail[period_detail.index(detail)].update(
                {"creditor_of": creditor_ofs}
            )
        detail_serializer = DetailSerializer(period_detail, many=True)
        period_serializer = PeriodSerializer(period)
        purchase_serializer = PurchaseSerializerForRead(
            all_periods_purchases, many=True
        )
        return Response(
            status=status.HTTP_200_OK,
            data={
                "period": period_serializer.data,
                "all_purchases": purchase_serializer.data,
                "detail": detail_serializer.data,
            },
        )


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PersonSerializer
    http_method_names = ["get", "post", "delete"]

    def perform_create(self, serializer):
        serializer.save()

    def destroy(self, request, pk=None):
        instance = self.get_object()
        if len(instance.period_set.all()) == 0:
            self.perform_destroy(instance=instance)
            return Response(
                status=status.HTTP_204_NO_CONTENT,
                data={RESPONSE_MESSAGES["successfully_deleted"]},
            )
        return Response(
            status=status.HTTP_403_FORBIDDEN,
            data={"detail": ERROR_MESSAGES["person_object_protected"]},
        )

    def list(self, request):
        persons = Person.objects.filter(owner=request.user)
        serializer = self.get_serializer(persons, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)


class PurchaseViewSet(viewsets.ModelViewSet):
    queryset = Purchase.objects.all()
    permission_classes = (IsAuthenticated, IsPurchaseOwner)
    serializer_class = PurchaseSerializer
    http_method_names = ["post", "get", "delete", "put"]

    def perform_create(self, serializer):
        serializer.save()

    def list(self, request):
        """
        function is used to list all purchases associated with a given period.
        """
        if "period" not in request.data:
            return Response(
                status=status.HTTP_400_BAD_REQUEST,
                data={"period": ERROR_MESSAGES["required_field"]},
            )
        period = get_object_or_404(Period, pk=request.data["period"])
        if period.owner != request.user:
            return Response(
                status=status.HTTP_403_FORBIDDEN,
                data=ERROR_MESSAGES["permission_denied"],
            )
        purchases = Purchase.objects.filter(period=period)
        serializer = PurchaseSerializer(purchases, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def perform_update(self, serializer):
        serializer.save()

    def destroy(self, request, pk=None):
        """Deletes a purchase object from the database.
        Returns a response with status code 204 (No Content) and a message indicating successful deletion.
        """
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={RESPONSE_MESSAGES["successfully_deleted"]},
        )

    def retrieve(self, request, pk=None):
        """Retrieve a purchase and its details from the database.
        retrieves a purchase object with the given primary key (pk) and calculates the details of the purchase using the purchase_detail_calculator function.
        """
        purchase = get_object_or_404(Purchase, pk=pk)
        data = purchase_detail_calculator(purchase=purchase)
        purchase_serializer = self.get_serializer(self.get_object())
        purchase_detail_serializer = DetailSerializer(data, many=True)
        return Response(
            status=status.HTTP_200_OK,
            data={
                "purchase": purchase_serializer.data,
                "detail": purchase_detail_serializer.data,
            },
        )

    # TODO: LOCALIZATION TRANSLATION
    # TODO: TEST
