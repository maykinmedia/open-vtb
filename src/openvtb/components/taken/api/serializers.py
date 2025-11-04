from rest_framework import serializers

from ..models import ExterneTaak


class ExterneTaakSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExterneTaak
        fields = "__all__"
