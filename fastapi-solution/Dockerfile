FROM python:3.10

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY requirements.txt .

RUN pip3 install --upgrade pip
RUN pip3 install -r requirements.txt --no-cache-dir

COPY ./src .
COPY ./entrypoint.sh .

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "main:app", "--bind", "0.0.0.0:8000", "-k", "uvicorn.workers.UvicornWorker"]