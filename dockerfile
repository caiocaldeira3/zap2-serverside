# syntax=docker/dockerfile:1
FROM python:3.10.0-alpine

LABEL version="1.0.0"
LABEL maintainer="Caio Caldeira"
LABEL app-name="Zap-2 ServerSide"

RUN apk add --no-cache gcc musl-dev linux-headers libffi-dev

ARG APP_PORT=5000
ARG APP_URL=127.0.0.1

ENV APP_PORT=$APP_PORT
ENV APP_URL=$APP_URL
ENV APP=run.py

RUN mkdir zap2-serverside

COPY . ./zap2-serverside

WORKDIR /zap2-serverside

RUN pip install -r requirements.build.txt
RUN pip install -r requirements.txt

WORKDIR /zap2-serverside/server
RUN ls

EXPOSE 5000

CMD [ "python", "run.py" ]