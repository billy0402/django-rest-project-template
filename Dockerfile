# Base Config
ARG PYTHON_VERSION=3.11.7
FROM python:${PYTHON_VERSION}-slim as base

# Tell Docker don't remove the apt cache
# ref: https://github.com/moby/buildkit/blob/master/frontend/dockerfile/docs/reference.md#example-cache-apt-packages
RUN rm -f /etc/apt/apt.conf.d/docker-clean; \
  echo 'Binary::apt::APT::Keep-Downloaded-Packages "true";' > /etc/apt/apt.conf.d/keep-cache


# Builder
FROM base as builder

WORKDIR /srv/app

ENV POETRY_HOME=/opt/poetry
ENV POETRY_VERSION=1.8.3

RUN \
  # Cache for apt
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  # Cache for pip
  --mount=type=cache,target=/root/.cache/pip \
  # Bind pyproject.toml and poetry.lock
  --mount=type=bind,source=pyproject.toml,target=pyproject.toml \
  --mount=type=bind,source=poetry.lock,target=poetry.lock \
  \
  # Install dependencies
  # apt-get update && \
  # apt-get install -y --no-install-recommends <package here> && \
  \
  # Install Poetry and export dependencies to requirements.txt
  python -m venv ${POETRY_HOME} && \
  ${POETRY_HOME}/bin/pip install --disable-pip-version-check --root-user-action=ignore poetry==${POETRY_VERSION} && \
  ${POETRY_HOME}/bin/poetry export --only main,deploy -o requirements.txt && \
  \
  # Install Python dependencies
  pip install --disable-pip-version-check --no-warn-script-location --root-user-action=ignore --user -r requirements.txt


# App
FROM base

RUN \
  # Cache for apt
  --mount=type=cache,target=/var/cache/apt,sharing=locked \
  --mount=type=cache,target=/var/lib/apt,sharing=locked \
  \
  # Install dependencies
  # - curl: for healthcheck
  apt-get update && \
  apt-get install -y --no-install-recommends curl

ARG USER=web

ENV HOME=/home/${USER}
ENV PATH=${HOME}/.local/bin:${PATH}

RUN useradd -s /bin/bash -m -d ${HOME} ${USER} && \
  mkdir ${HOME}/project && \
  mkdir ${HOME}/project/media && \
  chown -R ${USER}:${USER} ${HOME}/project

USER ${USER}

WORKDIR ${HOME}/project

COPY --chown=${USER}:${USER} --from=builder /root/.local ${HOME}/.local
COPY --chown=${USER}:${USER} --chmod=755 docker/run-server /usr/local/bin/run-server
COPY --chown=${USER}:${USER} server server
COPY --chown=${USER}:${USER} manage.py manage.py

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=3s --retries=3 \
  CMD curl -fs http://localhost:8000/api/v1/_/health || exit 1

CMD [ "run-server" ]
