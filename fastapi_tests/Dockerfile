FROM python:3.10

WORKDIR /tests

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip3 install --upgrade pip \
    & pip3 install -r requirements.txt --no-cache-dir

COPY . .

RUN chmod +x start.sh
RUN chmod +x functional/utils/wait-for-it.sh
RUN ls
CMD ./start.sh