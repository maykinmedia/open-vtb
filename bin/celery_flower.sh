#!/bin/bash
export OTEL_SERVICE_NAME="${OTEL_SERVICE_NAME:-openvtb-flower}"

exec celery flower --app openvtb --workdir src
