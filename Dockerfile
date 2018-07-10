FROM alpine
MAINTAINER Axel Bock <mr.axel.bock@gmail.com>

EXPOSE 5000

ENV BUILD_DEPS="python3-dev build-base linux-headers py3-pip"

ADD . /app

WORKDIR /app

RUN    apk add --no-cache $BUILD_DEPS python3 \
    && python3 -m ensurepip \
    && pip3 install -r requirements.txt \
    && apk del $BUILD_DEPS

CMD python3 flask_app.py
