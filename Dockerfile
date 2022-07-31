FROM python:3.10

ENV POETRY_VIRTUALENVS_CREATE false
ENV PIP_NO_CACHE_DIR off
ENV PIP_DISABLE_PIP_VERSION_CHECK on
ENV PYTHONUNBUFFERED 1

# RUN set -ex; \
#   apt-get update; \
#   # psycopg2 dependencies \
#   apt-get install -y libpq-dev; \
#   # git for codecov file listing \
#   apt-get install -y git; \
#   # cleaning up unused files \
#   apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false; \
#   rm -rf /var/lib/apt/lists/*

RUN pip install -U poetry

# Copy, then install requirements before copying rest for a requirements cache layer.
COPY pyproject.toml poetry.lock /tmp/
RUN set -ex; \
  cd /tmp; \
  poetry install

COPY . /app

ARG USER_ID=1001
ARG GROUP_ID=1001

RUN set -ex; \
  addgroup --gid $GROUP_ID --system containeruser; \
  adduser --system --uid $USER_ID --gid $GROUP_ID containeruser; \
  chown -R containeruser:containeruser /app
USER containeruser

WORKDIR /app
