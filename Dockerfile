# This is a multi-stage build file, which means a stage is used to build
# the backend (dependencies), the frontend stack and a final production
# stage re-using assets from the build stages. This keeps the final production
# image minimal in size.

# Stage 1 - Backend build environment
# includes compilers and build tooling to create the environment
FROM python:3.12-slim-bookworm AS backend-build

RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        pkg-config \
        build-essential \
        # only relevant when using editable/github dependencies, which is discouraged
        libpq-dev \
        shared-mime-info \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
RUN mkdir /app/src

# Use uv to install dependencies
RUN pip install uv -U
COPY ./requirements /app/requirements
RUN uv pip install --system -r requirements/production.txt


# Stage 2 - Install frontend deps and build assets
FROM node:24-alpine AS frontend-build

WORKDIR /app

# copy configuration/build files
COPY ./build /app/build/
COPY ./*.json ./*.js ./.babelrc /app/

# install WITH dev tooling
RUN npm ci --legacy-peer-deps

# copy source code
COPY ./src /app/src

# build frontend
RUN npm run build


# Stage 3 - Build docker image suitable for production
FROM python:3.12-slim-bookworm

# Stage 3.1 - Set up the needed production dependencies
# install all the dependencies for GeoDjango
RUN apt-get update && apt-get upgrade -y && apt-get install -y --no-install-recommends \
        procps \
        nano \
        mime-support \
        postgresql-client \
        gettext \
        shared-mime-info \
        gdal-bin \
        # lxml deps
        # libxslt \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY ./bin/docker_start.sh /start.sh
COPY ./bin/wait_for_db.sh /wait_for_db.sh
COPY ./bin/uwsgi.ini /
COPY ./bin/setup_configuration.sh /setup_configuration.sh
# Uncomment if you use celery
# COPY ./bin/celery_worker.sh /celery_worker.sh
# COPY ./bin/celery_beat.sh /celery_beat.sh
# COPY ./bin/celery_flower.sh /celery_flower.sh
RUN mkdir /app/bin /app/log /app/media

VOLUME ["/app/log", "/app/media"]

# copy backend build deps
COPY --from=backend-build /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=backend-build /usr/local/bin/uwsgi /usr/local/bin/uwsgi
# Uncomment if you use celery
# COPY --from=backend-build /usr/local/bin/celery /usr/local/bin/celery
COPY --from=backend-build /app/src/ /app/src/

# copy frontend build statics
COPY --from=frontend-build /app/src/openvtb/static /app/src/openvtb/static
COPY --from=frontend-build /app/node_modules/@fortawesome/fontawesome-free/webfonts /app/node_modules/@fortawesome/fontawesome-free/webfonts

# copy source code
COPY ./src /app/src

RUN groupadd -g 1000 maykin \
    && useradd -M -u 1000 -g 1000 maykin \
    && chown -R maykin:maykin /app

# drop privileges
USER maykin

ARG COMMIT_HASH RELEASE=latest
ENV RELEASE=${RELEASE} \
    GIT_SHA=${COMMIT_HASH} \
    PYTHONUNBUFFERED=1 \
    DJANGO_SETTINGS_MODULE=openvtb.conf.docker

ARG SECRET_KEY=dummy

LABEL org.label-schema.vcs-ref=$COMMIT_HASH \
      org.label-schema.vcs-url="https://github.com/maykinmedia/open-vtb" \
      org.label-schema.version=$RELEASE \
      org.label-schema.name="openvtb"

# Run collectstatic and compilemessages, so the result is already included in
# the image
RUN python src/manage.py collectstatic --noinput \
    && python src/manage.py compilemessages

EXPOSE 8000
CMD ["/start.sh"]
