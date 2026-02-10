#!/bin/bash
#
# Dump the current data into a fixtures, intended for demo data.
#
# You can load this fixture with:
# $ src/manage.py loaddata src/openvtb/fixtures/<file>
#
# Run this script from the root of the repository

OTEL_SDK_DISABLED=True src/manage.py dumpdata --indent=4 --natural-foreign --natural-primary verzoeken > src/openvtb/fixtures/verzoeken.json
OTEL_SDK_DISABLED=True src/manage.py dumpdata --indent=4 --natural-foreign --natural-primary taken > src/openvtb/fixtures/taken.json
OTEL_SDK_DISABLED=True src/manage.py dumpdata --indent=4 --natural-foreign --natural-primary berichten > src/openvtb/fixtures/berichten.json

