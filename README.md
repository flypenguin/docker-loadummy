# docker-loadummy

A simple little Flask app which computes pi to the nth number to simulate CPU load to test autoscaling on the cloud provider.

## Testing the flask app locally

    python flask_app.py

(of course flask has to be installed, so you should do it in a virtualenv)

## Environment variables

Displayed are the default values

```
COLOR=white         # a color name (see below), a color hex code, or "`random`"
STARTUP_TIME=0.0    # sleep that many seconds before flask starts
FLASK_PORT=80       # port flask listens on ()
FLASK_DEBUG=0       # whether flask is put in debug mode
FLASK_THREADED=1    # whether flask is being run multi-threaded
LOADUMMY_NAME=      # optional. set a name, useful for clusters - see below
LOADUMMY_NEXT=      # optional. documentation for this - see below
```

## Data encoding

The app will return HTML data (`Content-type: text/html`), unless otherwise specified in the `Accept:` header.
If it finds the string `yaml` in that header, YAML data is returned (`Content-type: application/x-yaml`, like rails),
if it finds the string `json` it returns JSON data (`Content-type: application/json`).

## Endpoints

|  endpoint                 |  description                                                     |
| ------------------------- | ---------------------------------------------------------------- |
| `/health`                 |   Returns "OK" with a HTTP status code of 200.                   |
| `/pi/<digits>`            | Computes the number pi with the number of digits given.          |
| `/env`                    | Displays all environment variables in the docker container.      |
| `/env/<VAR_START_STRING>` | Displays all environment variables starting with `VAR_START_STR` |
| `/distrib/<num>/<avg>`    | see below                                                        |

### Using the `/distrib` endpoint

Originally used to simulate load. Never really tried, but should work.

**To use this endpoint variable `LOADUMMY_DISTRIB` must be set:** `LOADUMMY_DISTRIB=https?://<next_host>[:<nextport>]`

Now, if you call `http://host:port/distrib/5/250` now, what happens then is ...

- it will create NUM requests for calculation of pi with
- (on average) DIGITS digits.

Or better: if you call it with `/5/250`, it might query those urls:

- `http://next_host:nextport/pi/267` (1st request)
- `http://next_host:nextport/pi/229` (2nd request)
- `http://next_host:nextport/pi/244` (...)
- `http://next_host:nextport/pi/231`
- `http://next_host:nextport/pi/276` (5th request)

... where the numbers are made up randomly around the 250 digits marker (plus minus 10%).

## Valid color names

|   color         |   color              |   color           |   color       |   color     |
| --------------- | -------------------- | ----------------- | ------------- | ----------- |
|  aliceblue      | darkslategray        | lightsalmon       | paleturquoise | yellow      |
|  antiquewhite   | darkturquoise        | lightsalmon       | palevioletred | yellowgreen |
|  aqua           | darkviolet           | lightseagreen     | papayawhip    |             |
|  aquamarine     | deeppink             | lightskyblue      | peachpuff     |             |
|  azure          | deepskyblue          | lightslategray    | peru          |             |
|  beige          | dimgray              | lightsteelblue    | pink          |             |
|  bisque         | dodgerblue           | lightyellow       | plum          |             |
|  black          | firebrick            | lime              | powderblue    |             |
|  blanchedalmond | floralwhite          | limegreen         | purple        |             |
|  blue           | forestgreen          | linen             | rebeccapurple |             |
|  blueviolet     | fuchsia              | magenta           | red           |             |
|  brown          | gainsboro            | maroon            | rosybrown     |             |
|  burlywood      | ghostwhite           | mediumaquamarine  | royalblue     |             |
|  cadetblue      | gold                 | mediumblue        | saddlebrown   |             |
|  chartreuse     | goldenrod            | mediumorchid      | salmon        |             |
|  chocolate      | gray                 | mediumpurple      | sandybrown    |             |
|  coral          | green                | mediumseagreen    | seagreen      |             |
|  cornflowerblue | greenyellow          | mediumslateblue   | seashell      |             |
|  cornsilk       | honeydew             | mediumspringgreen | sienna        |             |
|  crimson        | hotpink              | mediumturquoise   | silver        |             |
|  cyan           | indianred            | mediumvioletred   | skyblue       |             |
|  darkblue       | indigo               | midnightblue      | slateblue     |             |
|  darkcyan       | ivory                | mintcream         | slategray     |             |
|  darkgoldenrod  | khaki                | mistyrose         | snow          |             |
|  darkgray       | lavender             | moccasin          | springgreen   |             |
|  darkgreen      | lavenderblush        | navajowhite       | steelblue     |             |
|  darkkhaki      | lawngreen            | navy              | tan           |             |
|  darkmagenta    | lemonchiffon         | oldlace           | teal          |             |
|  darkolivegreen | lightblue            | olive             | thistle       |             |
|  darkorange     | lightcoral           | olivedrab         | tomato        |             |
|  darkorchid     | lightcyan            | orange            | turquoise     |             |
|  darkred        | lightgoldenrodyellow | orangered         | violet        |             |
|  darksalmon     | lightgray            | orchid            | wheat         |             |
|  darkseagreen   | lightgreen           | palegoldenrod     | white         |             |
|  darkslateblue  | lightpink            | palegreen         | whitesmoke    |             |
