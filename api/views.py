from django.shortcuts import get_object_or_404
from rest_framework import mixins, status, viewsets
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response

from .models import Period, PeriodShare, Person, Purchase
from .permissions import IsOwner, IsThroughPeriodRelatedOwner
from .responses import ERROR_MESSAGES, RESPONSE_MESSAGES
from .serializers import (DetailSerializer, PeriodSerializer,
                          PeriodShareSerializer, PersonSerializer,
                          PurchaseSerializer)
from .utils import calculate_period_detail, purchase_detail_calculator


class PeriodViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
):
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
        data = calculate_period_detail(period)
        return Response(status=status.HTTP_200_OK, data=data)


class PersonViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
):
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


class PurchaseViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
    mixins.RetrieveModelMixin,
):
    queryset = Purchase.objects.all()
    permission_classes = (IsAuthenticated, IsThroughPeriodRelatedOwner)
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


class PeriodShareViewSet(
    viewsets.GenericViewSet,
    mixins.CreateModelMixin,
    mixins.UpdateModelMixin,
    mixins.ListModelMixin,
    mixins.DestroyModelMixin,
):
    queryset = PeriodShare.objects.all()
    permission_classes = [IsAuthenticated, IsThroughPeriodRelatedOwner]
    serializer_class = PeriodShareSerializer
    http_method_names = ["get", "put", "post", "delete"]

    def perform_create(self, serializer) -> None:
        serializer.save()

    def perform_update(self, serializer) -> None:
        serializer.save()

    def list(self, request: Request) -> Response:
        period_share = PeriodShare.objects.filter(period__owner=request.user)
        serializer = self.get_serializer(period_share, many=True)
        return Response(status=status.HTTP_200_OK, data=serializer.data)

    def destroy(self, request: Request, pk=None) -> Response:
        instance = self.get_object()
        self.perform_destroy(instance=instance)
        return Response(
            status=status.HTTP_204_NO_CONTENT,
            data={"detail": RESPONSE_MESSAGES["successfully_deleted"]},
        )


class PeriodShareViewSetRetrieve(viewsets.GenericViewSet, mixins.RetrieveModelMixin):
    queryset = PeriodShare.objects.all()
    permission_classes = [AllowAny]
    serializer_class = PeriodShareSerializer
    http_method_names = ["get"]

    def retrieve(self, request: Request, pk=None) -> Response:
        try:
            instance = PeriodShare.objects.get(sharing_id=pk)
            if instance.is_expired():
                raise PeriodShare.DoesNotExist
            data = calculate_period_detail(instance.period)
            return Response(status=status.HTTP_200_OK, data=data)
        except PeriodShare.DoesNotExist:
            return Response(
                status=status.HTTP_401_UNAUTHORIZED,
                data={"detail": ERROR_MESSAGES["invalid_sharing_link"]},
            )

    # TODO: LOCALIZATION TRANSLATION
    # TODO: TEST
