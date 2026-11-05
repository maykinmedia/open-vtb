import datetime
import uuid

from django.utils import timezone

import factory
from factory.django import DjangoModelFactory
from faker import Faker

from openvtb.components.constants import HandelingsPerspectiefEnum

from ..models import Bericht, BerichtType, Bijlage, BijlageType

fake = Faker()


def get_random_urn(num_words: int = 1) -> str:
    return f"urn:maykin:{'-'.join(fake.words(nb=num_words))}:{uuid.uuid4()}"


class BerichtTypeFactory(DjangoModelFactory):
    handelings_perspectief = HandelingsPerspectiefEnum.BETALEN
    mijn_overheid_berichtenbox = True
    mijn_overheid_berichtenbox_type = "test"
    verantwoordelijke_organisatie = factory.LazyFunction(get_random_urn)

    class Meta:
        model = BerichtType

    @factory.post_generation
    def create_bijlagetype(obj, create, bijlagetype, **kwargs):
        if not create:
            return

        if bijlagetype:
            BijlageTypeFactory(bericht_type=obj)


class BerichtFactory(DjangoModelFactory):
    class Meta:
        model = Bericht

    bericht_type = factory.SubFactory(BerichtTypeFactory)
    ontvanger = factory.LazyFunction(get_random_urn)
    geopend_op = timezone.now()
    onderwerp = factory.Faker("word")
    referentie = factory.Faker("word")
    tekst = factory.Faker("sentence")
    publicatiedatum = timezone.now()
    einddatum_handelings_termijn = factory.LazyFunction(
        lambda: timezone.now() + datetime.timedelta(days=7)
    )

    @factory.post_generation
    def create_bijlage(obj, create, bijlage, **kwargs):
        if not create:
            return

        if bijlage:
            BijlageFactory(bericht=obj)


class BijlageTypeFactory(DjangoModelFactory):
    class Meta:
        model = BijlageType

    bericht_type = factory.SubFactory(BerichtTypeFactory)
    informatie_objecttype = factory.LazyFunction(get_random_urn)
    omschrijving = factory.Faker("sentence", nb_words=4)


class BijlageFactory(DjangoModelFactory):
    class Meta:
        model = Bijlage

    bericht = factory.SubFactory(BerichtFactory)
    informatie_object = factory.LazyFunction(get_random_urn)
    omschrijving = factory.Faker("word")
