# syntax=docker/dockerfile:1
###### Minimal image with base system requirements for most stages
FROM docker.io/ubuntu:20.04 AS minimal
LABEL maintainer="raccoongang.com <maksim.sokolskiy@raccoongang.com>"

ENV DEBIAN_FRONTEND=noninteractive
RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt,sharing=locked \ 
    apt update && \
    apt install -y curl git-core language-pack-en python3 python3-pip python3-venv \
    build-essential libcairo2 libffi-dev libmysqlclient-dev libxml2-dev libxslt-dev libjpeg-dev libssl-dev \
    pkg-config mysql-client
    ENV LC_ALL=en_US.UTF-8

ARG APP_USER_ID=1000
RUN if [ "$APP_USER_ID" = 0 ]; then echo "app user may not be root" && false; fi
RUN useradd --home-dir /rgg --create-home --shell /bin/bash --uid ${APP_USER_ID} app
USER ${APP_USER_ID}

ARG GAMMA_REPOSITORY=https://gitlab-ci-token:{{ CI_JOB_TOKEN }}@gitlab.raccoongang.com/products/rg-gamification/gamma.git
ARG GAMMA_VERSION=master
RUN git clone $GAMMA_REPOSITORY --branch $GAMMA_VERSION --depth 1 /rgg/gamma
WORKDIR /rgg/gamma

# Install python venv
RUN python3 -m venv ../venv/
ENV PATH="/rgg/venv/bin:$PATH"

RUN --mount=type=cache,target=/rgg/.cache/pip,sharing=shared pip install \
    setuptools==67.7.2 pip==23.1.2. wheel==0.40.0
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared pip install -r requirements.txt
RUN --mount=type=cache,target=/openedx/.cache/pip,sharing=shared pip install mysqlclient==2.2.4

FROM node:14 AS static

RUN mkdir /app

COPY --from=minimal /rgg/gamma /app

WORKDIR /app

RUN npm ci
RUN npm run build:prod

FROM minimal AS production

# # Install extra requirements
RUN --mount=type=cache,target=/rgg/.cache/pip,sharing=shared pip install \
    uwsgi==2.0.21

COPY --from=static /app/frontend/webpack_bundles frontend/webpack_bundles
COPY --from=static /app/webpack-stats-prod.json webpack-stats-prod.json

# Run production server
ENV DJANGO_SETTINGS_MODULE gamma.settings.production
RUN python manage.py collectstatic --noinput

EXPOSE 8000
CMD uwsgi \
    --static-map /static=/rgg/gamma/gamma/static \
    --static-map /media=/rgg/gamma/gamma/media \
    --http 0.0.0.0:8000 \
    --thunder-lock \
    --single-interpreter \
    --enable-threads \
    --processes=2 \
    --buffer-size=8192 \
    --wsgi-file gamma/wsgi.py


FROM node:14 AS static-dev

RUN mkdir /app

COPY --from=minimal /rgg/gamma /app

WORKDIR /app

RUN npm ci
RUN npm run build:dev

FROM minimal AS development

ENV DJANGO_SETTINGS_MODULE gamma.settings.devstack

COPY --from=static-dev /app/frontend/webpack_bundles frontend/webpack_bundles
COPY --from=static-dev /app/webpack-stats-dev.json webpack-stats-dev.json
