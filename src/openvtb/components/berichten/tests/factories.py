import datetime

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from ..models import Bericht, BerichtOntvanger


class BerichtOntvangerFactory(DjangoModelFactory):
    class Meta:
        model = BerichtOntvanger

    geadresseerde = "urn:nld:brp.bsn:111222333"
    geopend_op = timezone.now()


class BerichtFactory(DjangoModelFactory):
    class Meta:
        model = Bericht

    ontvanger = factory.SubFactory(BerichtOntvangerFactory)
    onderwerp = factory.Faker("sentence", nb_words=4)
    referentie = factory.Faker("word")
    bericht_tekst = factory.Faker("sentence")
    publicatiedatum = timezone.now()
    einddatum_handelings_termijn = factory.LazyFunction(
        lambda: timezone.now() + datetime.timedelta(days=7)
    )
