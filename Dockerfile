FROM --platform=$BUILDPLATFORM python:3.11-alpine

WORKDIR /APP

COPY requirements.txt /APP
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY src .

ENTRYPOINT ["python3"]
CMD ["main.py"]
