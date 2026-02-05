import datetime
import random
import string

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory

from ..models import Bericht

def get_random_urn():
    return f"urn:maykin:{''.join(random.choices(string.ascii_lowercase + string.digits, k=10))}"

class BerichtFactory(DjangoModelFactory):
    class Meta:
        model = Bericht

    ontvanger = factory.LazyFunction(get_random_urn)
    geopend_op = timezone.now()
    onderwerp = factory.Faker("sentence", nb_words=4)
    referentie = factory.Faker("word")
    bericht_tekst = factory.Faker("sentence")
    publicatiedatum = timezone.now()
    einddatum_handelings_termijn = factory.LazyFunction(
        lambda: timezone.now() + datetime.timedelta(days=7)
    )

    @factory.post_generation
    def create_bijlage(obj, create, bijlage, **kwargs):
        if not create:
            return

        if bijlage:
            BijlagenFactory(bericht=obj)


class BijlagenFactory(DjangoModelFactory):
    class Meta:
        model = Bijlage

    bericht = factory.SubFactory(BerichtFactory)
    informatie_object = factory.LazyFunction(get_random_urn)
    omschrijving = factory.Faker("sentence", nb_words=4)
