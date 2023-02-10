FROM --platform=$BUILDPLATFORM python:3.10-alpine

WORKDIR /src

COPY requirements.txt /src
RUN --mount=type=cache,target=/root/.cache/pip \
    pip3 install -r requirements.txt

COPY ./src/ /src

ENTRYPOINT ["python3"]
CMD ["main.py"]
