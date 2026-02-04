import datetime
import uuid

from freezegun import freeze_time
from rest_framework import status
from vng_api_common.tests import get_validation_errors, reverse

from openvtb.components.taken.constants import SoortTaak
from openvtb.components.taken.models import ExterneTaak
from openvtb.components.taken.tests.factories import FORM_IO, ADRES, ExterneTaakFactory
from openvtb.utils.api_testcase import APITestCase


@freeze_time("2026-01-01")
class FormulierTaakTests(APITestCase):
    list_url = reverse("taken:formuliertaak-list")

    def test_list(self):
        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 0)
        self.assertFalse(ExterneTaak.objects.exists())

        # create 1 formuliertaak
        ExterneTaakFactory.create(
            formuliertaak=True,
            niet_authentieke_persoonsgegevens=True,
        )

        response = self.client.get(self.list_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)

        formuliertaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "count": 1,
                "next": None,
                "previous": None,
                "results": [
                    {
                        "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(formuliertaak.uuid)})}",
                        "urn": f"urn:maykin:taken:externetaak:{str(formuliertaak.uuid)}",
                        "uuid": str(formuliertaak.uuid),
                        "titel": formuliertaak.titel,
                        "status": formuliertaak.status,
                        "startdatum": formuliertaak.startdatum.isoformat(),
                        "handelingsPerspectief": formuliertaak.handelings_perspectief,
                        "einddatumHandelingsTermijn": formuliertaak.einddatum_handelings_termijn.isoformat(),
                        "datumHerinnering": formuliertaak.datum_herinnering.isoformat(),
                        "toelichting": formuliertaak.toelichting,
                        "isToegewezenAan": {
                            "authentiekeVerwijzing": None,
                            "nietAuthentiekePersoonsgegevens": {
                                "voornaam": "Jan",
                                "achternaam": "Jansen",
                                "geboortedatum": "1980-05-15",
                                "emailadres": "jan.jansen@example.com",
                                "telefoonnummer": "+31612345678",
                                "postadres": ADRES,
                                "verblijfsadres": None,
                            },
                            "nietAuthentiekeOrganisatiegegevens": None,
                        },
                        "wordtBehandeldDoor": "",
                        "hoortBij": "",
                        "heeftBetrekkingOp": "",
                        "taakSoort": formuliertaak.taak_soort,
                        "details": {
                            "formulierDefinitie": formuliertaak.details[
                                "formulierDefinitie"
                            ],
                            "voorinvullenGegevens": formuliertaak.details[
                                "voorinvullenGegevens"
                            ],
                            "ontvangenGegevens": formuliertaak.details[
                                "ontvangenGegevens"
                            ],
                        },
                    },
                ],
            },
        )

        # create 1 betaaltaak
        ExterneTaakFactory.create(betaaltaak=True)

        # assert only 1 formuliertaak
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()["results"]), 1)
        self.assertEqual(
            response.json()["results"][0]["uuid"],
            str(formuliertaak.uuid),
        )

        # assert 2 total externeTaak
        self.assertEqual(ExterneTaak.objects.all().count(), 2)

    def test_detail(self):
        formuliertaak = ExterneTaakFactory.create(
            formuliertaak=True,
            niet_authentieke_persoonsgegevens=True,
        )
        detail_url = reverse(
            "taken:formuliertaak-detail",
            kwargs={"uuid": str(formuliertaak.uuid)},
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(formuliertaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(formuliertaak.uuid)}",
                "uuid": str(formuliertaak.uuid),
                "titel": formuliertaak.titel,
                "status": formuliertaak.status,
                "startdatum": formuliertaak.startdatum.isoformat(),
                "handelingsPerspectief": formuliertaak.handelings_perspectief,
                "einddatumHandelingsTermijn": formuliertaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": formuliertaak.datum_herinnering.isoformat(),
                "toelichting": formuliertaak.toelichting,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekePersoonsgegevens": formuliertaak.is_toegewezen_aan[
                        "nietAuthentiekePersoonsgegevens"
                    ],
                    "nietAuthentiekeOrganisatiegegevens": None,
                },
                "wordtBehandeldDoor": formuliertaak.wordt_behandeld_door,
                "hoortBij": formuliertaak.hoort_bij,
                "heeftBetrekkingOp": formuliertaak.heeft_betrekking_op,
                "taakSoort": formuliertaak.taak_soort,
                "details": {
                    "formulierDefinitie": formuliertaak.details["formulierDefinitie"],
                    "voorinvullenGegevens": formuliertaak.details[
                        "voorinvullenGegevens"
                    ],
                    "ontvangenGegevens": formuliertaak.details["ontvangenGegevens"],
                },
            },
        )

    def test_detail_not_found(self):
        # random uuid
        detail_url = reverse(
            "taken:externetaak-detail", kwargs={"uuid": str(uuid.uuid4())}
        )
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        # different taak_soort
        betaaltaak = ExterneTaakFactory.create(betaaltaak=True)
        detail_url = reverse(
            "taken:formuliertaak-detail",
            kwargs={"uuid": str(betaaltaak.uuid)},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_valid_create(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "formulierDefinitie": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
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
                    ],
                },
                "voorinvullenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                    },
                },
                "ontvangenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                        "date": datetime.date.today(),
                        "datetime": datetime.datetime.now(),
                    },
                },
            },
            "isToegewezenAan": {
                "nietAuthentiekeOrganisatiegegevens": {
                    "statutaireNaam": "Acme BV",
                    "bezoekadres": None,
                    "postadres": ADRES,
                    "emailadres": "info@acme.nl",
                    "telefoonnummer": "+31201234567",
                }
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        formuliertaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(formuliertaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(formuliertaak.uuid)}",
                "uuid": str(formuliertaak.uuid),
                "titel": formuliertaak.titel,
                "status": formuliertaak.status,
                "startdatum": formuliertaak.startdatum.isoformat(),
                "handelingsPerspectief": formuliertaak.handelings_perspectief,
                "einddatumHandelingsTermijn": formuliertaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": formuliertaak.datum_herinnering.isoformat(),
                "toelichting": formuliertaak.toelichting,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekePersoonsgegevens": None,
                    "nietAuthentiekeOrganisatiegegevens": formuliertaak.is_toegewezen_aan[
                        "nietAuthentiekeOrganisatiegegevens"
                    ],
                },
                "wordtBehandeldDoor": formuliertaak.wordt_behandeld_door,
                "hoortBij": formuliertaak.hoort_bij,
                "heeftBetrekkingOp": formuliertaak.heeft_betrekking_op,
                "taakSoort": formuliertaak.taak_soort,
                "details": {
                    "formulierDefinitie": formuliertaak.details["formulierDefinitie"],
                    "voorinvullenGegevens": formuliertaak.details[
                        "voorinvullenGegevens"
                    ],
                    "ontvangenGegevens": formuliertaak.details["ontvangenGegevens"],
                },
            },
        )

        # no ontvangenGegevens key
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "formulierDefinitie": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
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
                    ],
                },
                "voorinvullenGegevens": {
                    "textField": "Test value",
                },
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 2)
        formuliertaak = ExterneTaak.objects.get(uuid=response.json()["uuid"])
        self.assertEqual(formuliertaak.details["ontvangenGegevens"], {})

        # empty value ontvangenGegevens
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "formulierDefinitie": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
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
                    ],
                },
                "voorinvullenGegevens": {
                    "textField": "Test value",
                },
                "ontvangenGegevens": {},
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 3)
        formuliertaak = ExterneTaak.objects.get(uuid=response.json()["uuid"])
        self.assertEqual(formuliertaak.details["ontvangenGegevens"], {})

        # create form.io example TextField
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {
                "formulierDefinitie": FORM_IO,
                "voorinvullenGegevens": {
                    "textField": "Test value",
                },
                "ontvangenGegevens": {},
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 4)
        formuliertaak = ExterneTaak.objects.get(uuid=response.json()["uuid"])
        self.assertEqual(formuliertaak.details["formulierDefinitie"], FORM_IO)
        self.assertEqual(formuliertaak.details["ontvangenGegevens"], {})

        # test datumHerinnering auto filled
        # einddatumHandelingsTermijn - TAKEN_DEFAULT_REMINDER_IN_DAYS(7 days)
        self.assertEqual(formuliertaak.datum_herinnering, datetime.date(2026, 1, 3))

    def test_valid_create_with_external_relations(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "wordtBehandeldDoor": "urn:maykin:medewerker:brp:nnp:bsn:1234567892",
            "hoortBij": "urn:maykin:ztc:zaak:d42613cd-ee22-4455-808c-c19c7b8442a1",
            "heeftBetrekkingOp": "urn:maykin:product:cec996f4-2efa-4307-a035-32c2c9032e89",
            "details": {
                "formulierDefinitie": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
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
                    ],
                },
                "voorinvullenGegevens": {
                    "textField": "Test value",
                },
                "ontvangenGegevens": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
                        "date": datetime.date.today(),
                        "datetime": datetime.datetime.now(),
                    },
                },
            },
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        formuliertaak = ExterneTaak.objects.get()
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(formuliertaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(formuliertaak.uuid)}",
                "uuid": str(formuliertaak.uuid),
                "titel": formuliertaak.titel,
                "status": formuliertaak.status,
                "startdatum": formuliertaak.startdatum.isoformat(),
                "handelingsPerspectief": formuliertaak.handelings_perspectief,
                "einddatumHandelingsTermijn": formuliertaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": formuliertaak.datum_herinnering.isoformat(),
                "toelichting": formuliertaak.toelichting,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekeOrganisatiegegevens": None,
                    "nietAuthentiekePersoonsgegevens": None,
                },
                "wordtBehandeldDoor": formuliertaak.wordt_behandeld_door,
                "hoortBij": formuliertaak.hoort_bij,
                "heeftBetrekkingOp": formuliertaak.heeft_betrekking_op,
                "taakSoort": formuliertaak.taak_soort,
                "details": {
                    "formulierDefinitie": formuliertaak.details["formulierDefinitie"],
                    "voorinvullenGegevens": formuliertaak.details[
                        "voorinvullenGegevens"
                    ],
                    "ontvangenGegevens": formuliertaak.details["ontvangenGegevens"],
                },
            },
        )

    def test_invalid_create_required_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
        data = {}
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 3)
        self.assertEqual(
            get_validation_errors(response, "titel"),
            {
                "name": "titel",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "einddatumHandelingsTermijn"),
            {
                "name": "einddatumHandelingsTermijn",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertEqual(
            get_validation_errors(response, "details"),
            {
                "name": "details",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertFalse(ExterneTaak.objects.exists())

        # empty details values
        data = {
            "titel": "test",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "details": {},
        }
        response = self.client.post(self.list_url, data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(len(response.data["invalid_params"]), 1)
        self.assertEqual(
            get_validation_errors(response, "details.formulierDefinitie"),
            {
                "name": "details.formulierDefinitie",
                "code": "required",
                "reason": "Dit veld is vereist.",
            },
        )
        self.assertFalse(ExterneTaak.objects.exists())

    def test_valid_update_partial(self):
        formuliertaak = ExterneTaakFactory.create(formuliertaak=True)

        detail_url = reverse(
            "taken:formuliertaak-detail",
            kwargs={"uuid": str(formuliertaak.uuid)},
        )
        # empty PATCH
        response = self.client.patch(detail_url, {})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(formuliertaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(formuliertaak.uuid)}",
                "uuid": str(formuliertaak.uuid),
                "titel": formuliertaak.titel,
                "status": formuliertaak.status,
                "startdatum": formuliertaak.startdatum.isoformat(),
                "handelingsPerspectief": formuliertaak.handelings_perspectief,
                "einddatumHandelingsTermijn": formuliertaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": formuliertaak.datum_herinnering.isoformat(),
                "toelichting": formuliertaak.toelichting,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekeOrganisatiegegevens": None,
                    "nietAuthentiekePersoonsgegevens": None,
                },
                "wordtBehandeldDoor": formuliertaak.wordt_behandeld_door,
                "hoortBij": formuliertaak.hoort_bij,
                "heeftBetrekkingOp": formuliertaak.heeft_betrekking_op,
                "taakSoort": formuliertaak.taak_soort,
                "details": {
                    "formulierDefinitie": formuliertaak.details["formulierDefinitie"],
                    "voorinvullenGegevens": formuliertaak.details[
                        "voorinvullenGegevens"
                    ],
                    "ontvangenGegevens": formuliertaak.details["ontvangenGegevens"],
                },
            },
        )

        # PATCH externe_taak field
        response = self.client.patch(detail_url, {"titel": "new_title"})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        formuliertaak = ExterneTaak.objects.get()
        self.assertEqual(formuliertaak.titel, "new_title")

        # PATCH one field from json_data
        self.assertEqual(
            formuliertaak.details["formulierDefinitie"], FORM_IO
        )  # default factory value
        response = self.client.patch(
            detail_url,
            {
                "details": {
                    "formulierDefinitie": {
                        # test camelCase and snake_case
                        "key1": "value1",
                        "key2": {
                            "keyCamelCase": "value_2",
                            "key_snake_case": ["value_3"],
                        },
                        # required
                        "components": [
                            {
                                "type": "button",
                                "label": "Submit",
                                "key": "submit",
                                "disableOnInvalid": True,
                                "input": True,
                                "tableView": False,
                            },
                        ],
                    },
                    "voorinvullenGegevens": {
                        "textField": "Test value",
                    },
                }
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        formuliertaak = ExterneTaak.objects.get()
        self.assertEqual(
            formuliertaak.details["formulierDefinitie"],
            {
                "key1": "value1",
                "key2": {
                    "keyCamelCase": "value_2",
                    "key_snake_case": ["value_3"],
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
                ],
            },
        )
        self.assertEqual(
            formuliertaak.details["voorinvullenGegevens"],
            {"textField": "Test value"},
        )

        # update ontvangenGegevens
        self.assertEqual(
            formuliertaak.details["ontvangenGegevens"], {"key": "value"}
        )  # default
        response = self.client.patch(
            detail_url, {"details": {"ontvangenGegevens": {"new_key": "new_value"}}}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        formuliertaak = ExterneTaak.objects.get()
        # new value
        self.assertEqual(
            formuliertaak.details["ontvangenGegevens"], {"new_key": "new_value"}
        )
        self.assertNotEqual(formuliertaak.details["ontvangenGegevens"], FORM_IO)

        # patch isToegewezenAan with the new details
        response = self.client.patch(
            detail_url,
            {
                "isToegewezenAan": {
                    "authentiekeVerwijzing": {"urn": "urn:example:12345"}
                },
            },
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        formuliertaak = ExterneTaak.objects.get()
        self.assertEqual(
            formuliertaak.is_toegewezen_aan,
            {
                "authentiekeVerwijzing": {"urn": "urn:example:12345"},
            },
        )

    def test_valid_update(self):
        formuliertaak = ExterneTaakFactory.create(formuliertaak=True)

        detail_url = reverse(
            "taken:formuliertaak-detail",
            kwargs={"uuid": str(formuliertaak.uuid)},
        )

        # all required PUT fields
        response = self.client.put(
            detail_url,
            {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": {
                        "key1": "value1",
                        "key2": {
                            "keyCamelCase": "value_2",
                            "key_snake_case": ["value_3"],
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
                        ],
                    },
                    "voorinvullenGegevens": {
                        "textField": "Test value",
                    },
                },
            },
        )
        formuliertaak = ExterneTaak.objects.get()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.json(),
            {
                "url": f"http://testserver{reverse('taken:externetaak-detail', kwargs={'uuid': str(formuliertaak.uuid)})}",
                "urn": f"urn:maykin:taken:externetaak:{str(formuliertaak.uuid)}",
                "uuid": str(formuliertaak.uuid),
                "titel": formuliertaak.titel,
                "status": formuliertaak.status,
                "startdatum": formuliertaak.startdatum.isoformat(),
                "handelingsPerspectief": formuliertaak.handelings_perspectief,
                "einddatumHandelingsTermijn": formuliertaak.einddatum_handelings_termijn.isoformat(),
                "datumHerinnering": formuliertaak.datum_herinnering.isoformat(),
                "toelichting": formuliertaak.toelichting,
                "isToegewezenAan": {
                    "authentiekeVerwijzing": None,
                    "nietAuthentiekeOrganisatiegegevens": None,
                    "nietAuthentiekePersoonsgegevens": None,
                },
                "wordtBehandeldDoor": formuliertaak.wordt_behandeld_door,
                "hoortBij": formuliertaak.hoort_bij,
                "heeftBetrekkingOp": formuliertaak.heeft_betrekking_op,
                "taakSoort": formuliertaak.taak_soort,
                "details": {
                    "formulierDefinitie": formuliertaak.details["formulierDefinitie"],
                    "voorinvullenGegevens": formuliertaak.details[
                        "voorinvullenGegevens"
                    ],
                    "ontvangenGegevens": formuliertaak.details["ontvangenGegevens"],
                },
            },
        )
        self.assertEqual(
            formuliertaak.details["formulierDefinitie"],
            {
                "key1": "value1",
                "key2": {
                    "keyCamelCase": "value_2",
                    "key_snake_case": ["value_3"],
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
                ],
            },
        )

    def test_destroy(self):
        formuliertaak = ExterneTaakFactory.create(formuliertaak=True)

        detail_url = reverse(
            "taken:formuliertaak-detail",
            kwargs={"uuid": str(formuliertaak.uuid)},
        )

        self.assertEqual(ExterneTaak.objects.all().count(), 1)
        response = self.client.delete(detail_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        response = self.client.get(self.list_url)
        self.assertEqual(response.json()["count"], 0)
        self.assertFalse(ExterneTaak.objects.exists())


class FormulierTaakValidationTests(APITestCase):
    list_url = reverse("taken:formuliertaak-list")

    def test_invalid_create_pass_soort_taak(self):
        self.assertFalse(ExterneTaak.objects.exists())
        # wrong soort_taak
        data = {
            "titel": "titel",
            "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
            "taakSoort": SoortTaak.FORMULIERTAAK.value,
            "details": {
                "formulierDefinitie": {
                    "key1": "value1",
                    "key2": {
                        "keyCamelCase": "value_2",
                        "key_snake_case": ["value_3"],
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
                    ],
                },
                "voorinvullenGegevens": {
                    "textField": "Test value",
                },
            },
        }
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )
        # same soort_taak
        data["taak_soort"] = SoortTaak.BETAALTAAK.value
        response = self.client.post(self.list_url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )

    def test_invalid_update_partial(self):
        formuliertaak = ExterneTaakFactory.create(formuliertaak=True)

        detail_url = reverse(
            "taken:formuliertaak-detail",
            kwargs={"uuid": str(formuliertaak.uuid)},
        )
        # pass taak_soort
        response = self.client.patch(
            detail_url, {"taakSoort": SoortTaak.FORMULIERTAAK.value}
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data["code"], "invalid")
        self.assertEqual(response.data["title"], "Ongeldige invoerwaarde.")
        self.assertEqual(
            get_validation_errors(response, "taakSoort"),
            {
                "name": "taakSoort",
                "code": "invalid",
                "reason": "Dit veld wordt automatisch ingevuld; het kan niet worden geselecteerd.",
            },
        )

    def test_invalid_create_type_fields(self):
        self.assertFalse(ExterneTaak.objects.exists())
        with self.subTest("invalid start_date gt end_date"):
            data = {
                "titel": "test",
                "startdatum": datetime.date(2026, 1, 10),  # end < start
                "einddatumHandelingsTermijn": datetime.date(2025, 1, 10),
                "details": {
                    "formulierDefinitie": {
                        "key1": "value1",
                        "key2": {
                            "keyCamelCase": "value_2",
                            "key_snake_case": ["value_3"],
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
                        ],
                    },
                    "voorinvullenGegevens": {
                        "textField": "Test value",
                    },
                },
            }
            response = self.client.post(self.list_url, data)
            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "einddatumHandelingsTermijn"),
                {
                    "name": "einddatumHandelingsTermijn",
                    "code": "date-mismatch",
                    "reason": "startdatum should be before einddatum_handelings_termijn.",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("null value formulierDefinitie"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": None,
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.formulierDefinitie"),
                {
                    "name": "details.formulierDefinitie",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

    def test_invalid_formulier_definitie_schema(self):
        with self.subTest("formulierDefinitie invalid type"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": "",
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.formulierDefinitie"),
                {
                    "name": "details.formulierDefinitie",
                    "code": "invalid-json-schema",
                    "reason": "'' is not of type 'object'",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("formulierDefinitie is None"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": None,
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.formulierDefinitie"),
                {
                    "name": "details.formulierDefinitie",
                    "code": "null",
                    "reason": "Dit veld mag niet leeg zijn.",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("components required"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": {},
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(response, "details.formulierDefinitie"),
                {
                    "name": "details.formulierDefinitie",
                    "code": "invalid-json-schema",
                    "reason": "'components' is a required property",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("components invalid type"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": {"components": "test"},
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(
                    response, "details.formulierDefinitie.components"
                ),
                {
                    "name": "details.formulierDefinitie.components",
                    "code": "invalid-json-schema",
                    "reason": "'test' is not of type 'array'",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("components required 'label' field"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": {
                        "components": [
                            {},
                        ]
                    },
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(
                    response, "details.formulierDefinitie.components.0"
                ),
                {
                    "name": "details.formulierDefinitie.components.0",
                    "code": "invalid-json-schema",
                    "reason": "'label' is a required property",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("components required 'key' field"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": {
                        "components": [
                            {"label": "test"},
                        ]
                    },
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

            self.assertEqual(
                get_validation_errors(
                    response, "details.formulierDefinitie.components.0"
                ),
                {
                    "name": "details.formulierDefinitie.components.0",
                    "code": "invalid-json-schema",
                    "reason": "'key' is a required property",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())

        with self.subTest("components required 'type' field"):
            data = {
                "titel": "titel",
                "einddatumHandelingsTermijn": datetime.date(2026, 1, 10),
                "details": {
                    "formulierDefinitie": {
                        "components": [
                            {
                                "label": "test",
                                "key": "test",
                            },
                        ]
                    },
                },
            }
            response = self.client.post(self.list_url, data)

            self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
            self.assertEqual(
                get_validation_errors(
                    response, "details.formulierDefinitie.components.0"
                ),
                {
                    "name": "details.formulierDefinitie.components.0",
                    "code": "invalid-json-schema",
                    "reason": "'type' is a required property",
                },
            )
            self.assertFalse(ExterneTaak.objects.exists())
