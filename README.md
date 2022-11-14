# docker-loadummy

A simple little Flask app which computes pi to the nth number to simulate CPU load to test autoscaling on the cloud provider.

## Testing the flask app locally

    python flask_app.py

(of course flask has to be installed, so you should do it in a virtualenv)

## Environment variables

Displayed are the default values

```
COLOR=white         # a color name from ->gray_conversion.py or "random"
STARTUP_TIME=0.0    # sleep that many seconds before flask starts
FLASK_PORT=80       # port flask listens on ()
FLASK_DEBUG=0       # whether flask is put in debug mode
FLASK_THREADED=1    # whether flask is being run multi-threaded
LOADUMMY_NEXT=      # optional. documentation for this - see below.
```

## Data encoding

The app will return HTML data (`Content-type: text/html`), unless otherwise specified in the `Accept:` header.
If it finds the string `yaml` in that header, YAML data is returned (`Content-type: application/x-yaml`, like rails),
if it finds the string `json` it returns JSON data (`Content-type: application/json`).

## Endpoints

### `/health`

Returns "OK" with a HTTP status code of 200.

### `/pi/<digits>`

Computes the number pi with the number of digits given. So ...

    localhost:5000/pi/5000

... will compute pi until 5000 digits. On a MacBook Air 2012 100.000 digits will take about 20 seconds.

### `/env`

Displays all environment variables in the docker container.

### `/env/<VAR_START_STRING>`

Displays all environment variables starting with `VAR_START_STR`

    localhost:5000/env/PATH

### `/distrib/<num>/<avg>`

To simulate a controller / worker type of structure you can use the `/distrib/<a>/<b>` endpoint. To use this endpoint variable `LOADUMMY_DISTRIB` must be set.

    LOADUMMY_DISTRIB=https?://<next_host>[:<nextport>]

If you call `http://host:port/distrib/5/250` now, what happens then is ...

- it will create NUM requests for calculation of pi with
- (on average) DIGITS digits.

Or better: if you call it with `/5/250`, it might query those urls:

- `http://next_host:nextport/pi/267` (1st request)
- `http://next_host:nextport/pi/229` (2nd request)
- `http://next_host:nextport/pi/244` (...)
- `http://next_host:nextport/pi/231`
- `http://next_host:nextport/pi/276` (5th request)

... where the numbers are made up randomly around the 250 digits marker (plus minus 10%).
