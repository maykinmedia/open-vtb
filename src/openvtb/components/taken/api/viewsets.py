from rest_framework import viewsets

from ..models import ExterneTaak
from .serializers import ExterneTaakSerializer


class ExterneTaakViewSet(viewsets.ModelViewSet):
    queryset = ExterneTaak.objects.all()
    serializer_class = ExterneTaakSerializer
