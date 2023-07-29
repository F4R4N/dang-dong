from rest_framework import viewsets, status
from rest_framework.views import APIView
from .serializers import PeriodSerializer, PersonSerializer, PurchaseSerializer
from .models import Period, Person, Purchase
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .permissions import IsOwner
from .responses import RESPONSE_MESSAGES


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PeriodSerializer

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


class PersonViewSet(viewsets.ModelViewSet):
    queryset = Person.objects.all()
    permission_classes = (IsAuthenticated, IsOwner)
    serializer_class = PersonSerializer

    def perform_create(self, serializer):
        serializer.save()

    # FIXME: REMEMBER TO IMPLIMENT THIS, THE ONLY THING THA CAN BE EDITED SHOULD BE TEH COEFFICIENT OF COEFFICIENT OBJECT
    # def perform_update(self, serializer):
    #     serializer.save()

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

    def perform_create(self, serializer):
        serializer.save()
    