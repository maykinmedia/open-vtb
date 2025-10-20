#!/bin/bash

set -e

LOGLEVEL=${CELERY_LOGLEVEL:-INFO}

export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-openvtb-scheduler}"

mkdir -p celerybeat

echo "Starting celery beat"
exec celery beat \
    --app openvtb \
    -l $LOGLEVEL \
    --workdir src \
    -s ../celerybeat/beat
