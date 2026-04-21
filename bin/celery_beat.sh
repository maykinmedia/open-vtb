#!/bin/bash

set -e

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

# Set defaults for OTEL
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-openvtb-scheduler}"

mkdir -p celerybeat

echo "Starting celery beat"
exec celery --app openvtb.celery --workdir src beat \
    -l $LOGLEVEL \
    -s ../celerybeat/beat
