###########
# BUILDER #
###########

# pull official base image
FROM --platform=$BUILDPLATFORM python:3.11-alpine as builder

# set work directory
WORKDIR /usr/src/app

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# install python dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt .
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt



FROM --platform=$BUILDPLATFORM python:3.11-alpine

# create directory for the app user
RUN mkdir -p /home/app

# create the app user
RUN addgroup -S appgroup && adduser -S app -G appgroup

# create the appropriate directories
ENV HOME=/home/app
ENV APP_HOME=/home/app/web
RUN mkdir $APP_HOME
WORKDIR $APP_HOME

# install dependencies
COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*
RUN pip install -r requirements.txt

# copy entrypoint
COPY ./entrypoint.sh $APP_HOME

# copy project
COPY src $APP_HOME

# chown all the files to the app user
RUN chown -R app:appgroup $APP_HOME

# change to the app user
USER app

# run entrypoint.sh
ENTRYPOINT ["/home/app/web/entrypoint.sh"]
CMD ["python", "main.py"]
