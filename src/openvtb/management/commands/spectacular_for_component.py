from drf_spectacular.management.commands import spectacular

SCHEMA_MAPPING = {
    "custom_settings": "openvtb.components.{}.api.schema.custom_settings",
    "urlconf": "openvtb.components.{}.api.urls",
}


class Command(spectacular.Command):
    def add_arguments(self, parser):
        super().add_arguments(parser)

        parser.add_argument(
            "--component",
            dest="component",
            required=True,
            help="The component name to define urlconf and schema info",
        )

    def handle(self, *args, **options):
        component = options.pop("component").replace("/", ".")

        # rewrite command arguments based on the component
        options["custom_settings"] = SCHEMA_MAPPING["custom_settings"].format(component)
        options["urlconf"] = SCHEMA_MAPPING["urlconf"].format(component)
        super().handle(*args, **options)
