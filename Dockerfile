FROM python:2-onbuild
MAINTAINER Axel Bock <mr.axel.bock@gmail.com>

EXPOSE 5000

ADD . /flask
WORKDIR /flask
CMD python flask_app.py
