FROM python:3.11-alpine
LABEL maintainer="Axel Bock <ab@a3b3.de>"

EXPOSE 80

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV FLASK_PORT=80

CMD [ "python", "./flask_app.py" ]
