from rest_framework import viewsets
from .serializers import PeriodSerializer
from .models import Period
from rest_framework.permissions import IsAuthenticated


class PeriodViewSet(viewsets.ModelViewSet):
    queryset = Period.objects.all()
    permission_classes = (IsAuthenticated, )
    serializer_class = PeriodSerializer

    def perform_create(self, serializer):
        serializer.save()
