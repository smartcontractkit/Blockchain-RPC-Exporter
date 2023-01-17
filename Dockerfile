
FROM python:3.10-slim@sha256:ff4f0ce0074b0876f6d39ddfc32910557561ff061d13dc538879658c589bf936 AS build

WORKDIR /app
# Copy repository files
COPY setup.py .
COPY src/*.py src/
COPY src/tests src/tests

RUN pip install -e ".[test]"
# Execute tests
WORKDIR src/
RUN pytest

RUN rm -f /src/tests
RUN rm -f test_*

CMD ["brpc"]
