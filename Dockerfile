FROM ubuntu:24.04

WORKDIR /usr/src/app
COPY . /usr/src/app

ENV WANDB_API_KEY=934436ad14ceb55b75a7917bc289ec0ac28246e2 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=true \
    POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache \
    DEBIAN_FRONTEND=noninteractive

RUN apt update && \
    apt install software-properties-common -y && \
    add-apt-repository ppa:graphics-drivers && \
    add-apt-repository ppa:deadsnakes/ppa && \
    apt update && \
    apt install nvidia-driver-535 -y --no-install-recommends && \
    apt install python3.11 python3-pip python3-poetry -y --no-install-recommends && \
    apt-get autoremove --yes && \
    apt-get purge --yes software-properties-common && \
    rm -rf /var/lib/apt/lists/*

RUN poetry install --without dev && rm -rf $POETRY_CACHE_DIR
CMD ["poetry", "run", "python", "--help"]
