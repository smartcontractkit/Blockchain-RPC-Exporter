FROM python:3.11.1 AS build
COPY requirements.txt .
RUN pip install -r ./requirements.txt

FROM gcr.io/distroless/python3:nonroot

COPY --from=build /usr/local/lib/python3.9/site-packages/ \
 /usr/lib/python3.9/.

ENV LC_ALL C.UTF-8
WORKDIR /usr/src/app
COPY src/*.py .
COPY src/collectors/* collectors/
# https://github.com/GoogleContainerTools/distroless/blob/main/experimental/python3/BUILD#L77
USER nonroot
CMD ["exporter.py"]
