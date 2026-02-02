from django.utils import timezone

import factory

from ..constants import ActionTaak, SoortTaak
from ..models import ExterneTaak

FORM_IO = {
    "display": "form",
    "settings": {
        "pdf": {
            "id": "1ec0f8ee-6685-5d98-a847-26f67b67d6f0",
            "src": "https://files.form.io/pdf/5692b91fd1028f01000407e3/file/1ec0f8ee-6685-5d98-a847-26f67b67d6f0",
        }
    },
    "components": [
        {
            "type": "button",
            "label": "Submit",
            "key": "submit",
            "disableOnInvalid": True,
            "input": True,
            "tableView": False,
        },
        {
            "label": "Text Field",
            "placeholder": "Add Test",
            "description": "Description ",
            "tooltip": "Tooltip",
            "prefix": "Test",
            "applyMaskOn": "change",
            "tableView": True,
            "validateWhenHidden": False,
            "key": "textField",
            "type": "textfield",
            "input": True,
        },
    ],
}


class ExterneTaakFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = ExterneTaak

    titel = factory.Faker("sentence")
    handelings_perspectief = ActionTaak.LEZEN
    einddatum_handelings_termijn = factory.LazyFunction(
        lambda: timezone.now() + timezone.timedelta(days=7)
    )

    class Params:
        betaaltaak = factory.Trait(
            taak_soort=SoortTaak.BETAALTAAK,
            details={
                "bedrag": "10.12",
                "valuta": "EUR",
                "transactieomschrijving": "test",
                "doelrekening": {
                    "naam": "test",
                    "code": "123-ABC",
                    "iban": "NL18BANK23481326",
                },
            },
        )
        gegevensuitvraagtaak = factory.Trait(
            taak_soort=SoortTaak.GEGEVENSUITVRAAGTAAK,
            details={
                "uitvraagLink": "http://example.com/",
                "voorinvullenGegevens": {
                    "key": "value",
                },
                "ontvangenGegevens": {
                    "key": "value",
                },
            },
        )
        formuliertaak = factory.Trait(
            taak_soort=SoortTaak.FORMULIERTAAK,
            details={
                "formulierDefinitie": FORM_IO,
                "voorinvullenGegevens": {
                    "textField": "Test value",
                },
                "ontvangenGegevens": {
                    "key": "value",
                },
            },
        )
