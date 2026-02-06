import datetime

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from ..models import Bericht


class BerichtFactory(DjangoModelFactory):
    class Meta:
        model = Bericht

    ontvanger = "urn:nld:brp.bsn:111222333"
    geopend_op = timezone.now()
    onderwerp = factory.Faker("sentence", nb_words=4)
    referentie = factory.Faker("word")
    bericht_tekst = factory.Faker("sentence")
    publicatiedatum = timezone.now()
    einddatum_handelings_termijn = factory.LazyFunction(
        lambda: timezone.now() + datetime.timedelta(days=7)
    )
