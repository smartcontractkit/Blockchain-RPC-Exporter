FROM python:3.11-slim AS base

WORKDIR /opt/brpc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


FROM base AS test

COPY requirements-dev.txt .
RUN pip install --no-cache-dir -r requirements-dev.txt

COPY src/*.py ./
COPY src/tests tests

RUN coverage run --branch -m pytest
RUN coverage report --fail-under 90
RUN pylint *.py

FROM base AS prod

COPY src/*.py ./

RUN useradd -r -s /sbin/nologin -u 999 nonroot
USER nonroot
EXPOSE 8080
CMD [ "python", "exporter.py" ]
