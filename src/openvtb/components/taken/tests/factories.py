import datetime

import factory

from ..constants import SoortTaak
from ..models import ExterneTaak

ADRES = {
    "woonplaats": "Amsterdam",
    "postcode": "1000 AB",
    "huisnummer": "12",
    "huisletter": "A",
    "huisnummertoevoeging": "bis",
}

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
    handelings_perspectief = "lezen"
    einddatum_handelings_termijn = factory.LazyFunction(
        lambda: datetime.date.today() + datetime.timedelta(days=7)
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

        # is_toegewezen_aan type
        authentieke_verwijzing = factory.Trait(
            is_toegewezen_aan={
                "authentiekeVerwijzing": {
                    "urn": "urn:nld:brp:bsn:111222333",
                }
            }
        )
        niet_authentieke_persoonsgegevens = factory.Trait(
            is_toegewezen_aan={
                "nietAuthentiekePersoonsgegevens": {
                    "voornaam": "Jan",
                    "achternaam": "Jansen",
                    "geboortedatum": "1980-05-15",
                    "emailadres": "jan.jansen@example.com",
                    "telefoonnummer": "+31612345678",
                    "postadres": ADRES,
                    "verblijfsadres": None,
                }
            }
        )
        niet_authentieke_organisatiegegevens = factory.Trait(
            is_toegewezen_aan={
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": None,
                    "postadres": ADRES,
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                }
            }
        )
