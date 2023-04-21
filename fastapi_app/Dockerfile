FROM python:3.11-slim-bullseye

ARG POETRY_VERSION=1.4.2

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=off \
    PIP_DEFAULT_TIMEOUT=100 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    POETRY_VIRTUALENVS_IN_PROJECT=false \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_NO_INTERACTION=1

# system dependencies
RUN apt update \
    && apt install --no-install-recommends -y \
    git \
    build-essential

# app setup
WORKDIR /code
COPY ./poetry.lock ./pyproject.toml /code/

# project dependencies
RUN --mount=type=cache,target=/root/.cache pip install -U pip setuptools
RUN --mount=type=cache,target=/root/.cache pip install poetry==${POETRY_VERSION}
RUN poetry config virtualenvs.create false
RUN --mount=type=cache,target=/root/.cache poetry install --no-root --no-interaction

# cleanup
RUN apt purge -y \
    git \
    build-essential

# copy main project
COPY . /code

# listen port
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
