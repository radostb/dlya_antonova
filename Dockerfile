FROM python:3.8-slim as python-base

ENV PYTHONUNBUFFERED=1 \
	PYTHONDONTWRITEBYTECODE=1 \
	PIP_NO_CACHE_DIR=OFF \
	PIP_DISABLE_PIP_VERSION_CHECK=ON \
	PIP_DEFAULT_TIMEOUT=100 \
	POETRY_VERSION=1.0.5 \
	POETRY_HOME="../.poetry" \
	POETRY_VIRTUALENVS_IN_PROJECT=true \
	POETRY_NO_INTERACTION=1 \
	PYSETUP_PATH="/robot_dlya_antonova" \
	VENV_PATH="/robot_dlya_antonova/.venv"

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

FROM python-base as builder-base
RUN apt-get update \
	&& apt-get install --no-install-recommends -y \
	curl \
	build-essential

RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | python

WORKDIR $PYSETUP_PATH
COPY poetry.lock pyproject.toml ./

RUN poetry install

FROM python-base as production
COPY --from=builder-base $PYSETUP_PATH $PYSETUP_PATH

COPY robot_dlya_antonova/ .

EXPOSE 9000 35729


CMD ["python","./robot.py"]



