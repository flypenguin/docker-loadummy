# docker-loadummy

A super little Flask app which computes pi to the nth number
to simulate CPU load to test autoscaling on the cloud provider.


## Testing the flask app locally

    python flask_app.py

(of course flask has to be installed, so you should do it in a virtualenv)


## Container environment variables

To start flask multi-threaded (so that more than one request can be answered by one instance at the same time) just set the `FLASK_THREADED` environment variable to either "1", "on" or "true" (case does not matter).


## Available endpoints


### `/pi/<digits>`

Computes the number pi with the number of digits given. So ...

    localhost:5000/pi/5000

... will compute pi until 5000 digits. On a MacBook Air 2012 100.000 digits will take about 20 seconds.


### `/env`

Displays all environment variables in the docker container.


### `/env/<VAR_START_STRING>`

Displays all environment variables starting with `VAR_START_STR`

    localhost:5000/env/PATH

