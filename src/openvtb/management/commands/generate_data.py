"""
Generate test data for Open VTB: verzoeken, taken and berichten.

Examples:
    python manage.py generate_test_data
    python manage.py generate_test_data --resources verzoeken --resources taken
    python manage.py generate_test_data --count 5000
"""

import time
from enum import Enum
from typing import Annotated

from django.contrib.auth import get_user_model
from django.db import transaction
from django.db.models import Model

import typer
from django_typer.management import TyperCommand

from openvtb.accounts.tests.factories import UserFactory

User = get_user_model()
BULK_BATCH_SIZE = 1000
AUTH_TOKEN = "performance_token"


class Resource(str, Enum):
    verzoeken = "verzoeken"
    taken = "taken"
    berichten = "berichten"


DEFAULT_RESOURCES = list(Resource)


def bulk_create(objects: list[Model]) -> list[Model]:
    if not objects:
        return []
    model = type(objects[0])
    return model.objects.bulk_create(objects, batch_size=BULK_BATCH_SIZE)


class Command(TyperCommand):
    help = "Generate test data (verzoeken, taken, berichten) using the factories."

    def handle(
        self,
        resources: Annotated[
            list[Resource],
            typer.Option("--resources", help="Resources to create (repeatable)."),
        ] = DEFAULT_RESOURCES,
        count: Annotated[
            int,
            typer.Option(help="Number of objects to create per resource.", min=1),
        ] = 500,
        token: Annotated[
            str, typer.Option(help="Token of the load test user.")
        ] = AUTH_TOKEN,
    ) -> None:
        generators = {
            Resource.verzoeken: self.generate_verzoeken,
            Resource.taken: self.generate_taken,
            Resource.berichten: self.generate_berichten,
        }
        selected = [resource for resource in Resource if resource in resources]
        self.stdout.write(
            f"Generating test data: {count} objects per resource "
            f"({', '.join(r.value for r in selected)})"
        )

        total_start = time.perf_counter()

        if token:
            self.stdout.write("")
            self.stdout.write(self.style.MIGRATE_HEADING("User and token"))
            # use token string for username, password and key
            self.recreate_user_and_token(token)

        with transaction.atomic():
            for resource in selected:
                self.stdout.write("")
                self.stdout.write(
                    self.style.MIGRATE_HEADING(resource.value.capitalize())
                )

                start = time.perf_counter()
                totals = generators[resource](count)
                elapsed = time.perf_counter() - start
                self.stdout.write(f" Totals {totals} done in {elapsed:.2f}s")

        total_elapsed = time.perf_counter() - total_start
        self.stdout.write(
            self.style.SUCCESS(f"Test data generated in {total_elapsed:.2f}s")
        )

    @staticmethod
    def _create_type(type_factory, count: int, **kwargs):
        from factory.fuzzy import FuzzyChoice

        types = type_factory.create_batch(max(1, count // 4), **kwargs)
        return FuzzyChoice(types)

    def recreate_user_and_token(self, token: str) -> None:
        """
        Delete the load test user and token, and create them again
        """
        from openvtb.accounts.tests.factories import TokenFactory

        User = UserFactory._meta.model
        Token = TokenFactory._meta.model

        tokens_deleted, _ = Token.objects.filter(key=token).delete()
        users_deleted, _ = User.objects.filter(username=token).delete()
        if tokens_deleted or users_deleted:
            self.stdout.write(f"  Deleted existing user {token!r} and token {token!r}")

        user = UserFactory.create(
            username=token,
            password=token,
            is_staff=True,
            is_superuser=True,
        )
        TokenFactory.create(key=token, user=user)
        self.stdout.write(f"  Created superuser {token!r} with token {token!r}")

    def generate_verzoeken(self, count: int) -> int:
        from openvtb.components.verzoeken.tests.factories import (
            BijlageFactory,
            VerzoekBetalingFactory,
            VerzoekBronFactory,
            VerzoekFactory,
            VerzoekTypeFactory,
        )

        verzoek_type = self._create_type(VerzoekTypeFactory, count, create_versie=True)
        verzoeken = bulk_create(
            VerzoekFactory.build_batch(count, verzoek_type=verzoek_type)
        )

        bulk_create([BijlageFactory.build(verzoek=verzoek) for verzoek in verzoeken])
        bulk_create(
            [VerzoekBronFactory.build(verzoek=verzoek) for verzoek in verzoeken]
        )
        bulk_create(
            [VerzoekBetalingFactory.build(verzoek=verzoek) for verzoek in verzoeken]
        )

        return len(verzoeken)

    def generate_taken(self, count: int) -> int:
        from openvtb.components.taken.tests.factories import ExterneTaakFactory

        TAAK_TYPES = ("betaaltaak", "urltaak", "formuliertaak")

        per_type, remainder = divmod(count, len(TAAK_TYPES))
        taken = []
        for index, taak_type in enumerate(TAAK_TYPES):
            batch_size = per_type + (1 if index < remainder else 0)
            taken += ExterneTaakFactory.build_batch(batch_size, **{taak_type: True})

        return len(bulk_create(taken))

    def generate_berichten(self, count: int) -> int:
        from openvtb.components.berichten.tests.factories import (
            BerichtFactory,
            BerichtTypeFactory,
            BijlageFactory,
        )

        bericht_type = self._create_type(BerichtTypeFactory, count)
        berichten = bulk_create(
            BerichtFactory.build_batch(count, bericht_type=bericht_type)
        )
        bulk_create([BijlageFactory.build(bericht=bericht) for bericht in berichten])

        return len(berichten)
