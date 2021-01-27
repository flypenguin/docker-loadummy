FROM python3.9-alpine
LABEL maintainer="Axel Bock <mr.axel.bock@gmail.com>"

EXPOSE 5000

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./flask_app.py" ]
