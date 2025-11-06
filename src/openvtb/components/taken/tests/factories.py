from django.utils import timezone

import factory

from ..constants import SoortTaak
from ..models import ExterneTaak


class ExterneTaakFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExterneTaak

    titel = factory.Faker("sentence")
    handelings_perspectief = factory.Faker("word")
    einddatum_handelings_termijn = factory.LazyFunction(
        lambda: timezone.now() + timezone.timedelta(days=7)
    )

    class Params:
        betaaltaak = factory.Trait(
            taak_soort=SoortTaak.BETAALTAAK,
            data={
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "iban": "NL18BANK23481326",
                },
            },
        )
        gegevensuitvraagtaak = factory.Trait(
            taak_soort=SoortTaak.GEGEVENSUITVRAAGTAAK,
            data={
                "uitvraagLink": "http://example.com/",
                "ontvangenGegevens": {
                    "key": "value",
                },
            },
        )
        formuliertaak = factory.Trait(
            taak_soort=SoortTaak.FORMULIERTAAK,
            data={
                "formulierDefinitie": {
                    "key": "value",
                },
                "ontvangenGegevens": {
                    "key": "value",
                },
            },
        )
