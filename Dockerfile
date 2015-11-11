FROM flypenguin/simple_flask
MAINTAINER Axel Bock <mr.axel.bock@gmail.com>

ADD . /flask
WORKDIR /flask
CMD python flask_app.py
