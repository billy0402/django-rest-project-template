# Base Config
ARG PYTHON_VERSION=3.11.7
FROM python:${PYTHON_VERSION}-slim as base


# Builder
FROM base as builder

WORKDIR /srv/app

COPY pyproject.toml pyproject.toml
COPY poetry.lock poetry.lock

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.7.1

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install -y --no-install-recommends gcc python3-dev \
  \
  && python -m venv ${POETRY_HOME} \
  && ${POETRY_HOME}/bin/pip --no-cache-dir --disable-pip-version-check install poetry==${POETRY_VERSION} \
  && ${POETRY_HOME}/bin/poetry export --with deploy -o requirements.txt \
  && pip install --no-cache-dir --disable-pip-version-check --no-warn-script-location --user -r requirements.txt \
  \
  && apt-get clean autoclean \
  && apt-get autoremove --yes \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/


# App
FROM base

RUN export DEBIAN_FRONTEND=noninteractive \
  && apt-get update \
  && apt-get install -y --no-install-recommends curl \
  \
  && apt-get clean autoclean \
  && apt-get autoremove --yes \
  && rm -rf /var/lib/{apt,dpkg,cache,log}/

ARG USER=web

ENV HOME=/home/${USER}
ENV PATH=${HOME}/.local/bin:${PATH}

RUN useradd -s /bin/bash -m -d ${HOME} ${USER} \
  && mkdir ${HOME}/project \
  && mkdir ${HOME}/project/media \
  && chown -R ${USER}:${USER} ${HOME}/project

WORKDIR ${HOME}/project

USER ${USER}

COPY --chown=${USER}:${USER} --from=builder /root/.local ${HOME}/.local

COPY --chown=${USER}:${USER} --chmod=755 docker/run-server /usr/local/bin/run-server

COPY --chown=${USER}:${USER} server server
COPY --chown=${USER}:${USER} manage.py manage.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -fs http://localhost:8000/api/v1/_/health || exit 1

CMD [ "run-server" ]
