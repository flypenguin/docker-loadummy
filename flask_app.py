from flask import Flask
import flask, picompute, time, os, socket
from jinja2 import escape
import datetime as dt

app = Flask(__name__)
app.debug = True
threaded = None

def _get_env_vars(var_start=''):
    render = unicode("")
    for key in sorted(os.environ.keys()):
        if not key.startswith(var_start): continue
        val = os.environ.get(key)
        addme = escape(("%s = %s"%(key,val)).decode('utf-8'))
        # the "str()" is necessary, otherwise this is (probably) some
        # convenience object which auto-escapes everything you add to it ...
        render += unicode(addme) + "<br>"
    return render

def _get_host_ip():
    import socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('google.com', 0))
    return s.getsockname()[0]


@app.route('/')
def hello_world():
    global threaded
    color = "green" if threaded else "red"
    enabled = "ENABLED" if threaded else "disabled"
    rv = """
<table>
    <tr>
        <td>hostname</td>
        <td>{}</td>
    </tr>
    <tr>
        <td>ip address</td>
        <td>{}</td>
    </tr>
    <tr>
        <td>multi threading</td>
        <td>{}</td>
    </tr>
    <tr>
        <td>available endpoints</td>
        <td>{}</td>
    </tr>
</table>
""".format(
        socket.gethostname(),
        _get_host_ip(),
        "<span style=\"color:%s\">%s</span>"%(color, enabled),
        str(flask.escape("/pi/<digits>, /env, /env/<variable_start_string>"))
    )
    return rv

@app.route('/pi/<digits>')
def compute_digits(digits):
    dt_str = str(dt.datetime.now())
    begin  = time.time()
    computed_str = str(picompute.pi(int(digits)))[-10:]
    duration = time.time() - begin
    return "<p>Time: " + dt_str + \
        "</p><p>Number of digits computed: " + str(digits) + \
        "</p><p>Last 10 digits: " + computed_str + \
        "</p><p>Computing duration: " + str(duration) + "</p>"

@app.route('/env')
def full_env():
    return _get_env_vars()

@app.route('/env/<start>')
def selected_env(start):
    return _get_env_vars(start)


if __name__ == '__main__':
    threaded = os.environ.get('FLASK_THREADED')
    if threaded and threaded.lower() in ("1", "true", "on"):
        threaded = True
    else:
        threaded = False
    app.run(host='0.0.0.0', threaded=threaded)
