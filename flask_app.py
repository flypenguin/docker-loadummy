from flask import Flask, request, make_response, render_template, redirect
from jinja2 import escape
import requests, picompute, time, os, socket, uuid, datetime, yaml, random, json, threading, subprocess
import datetime as dt
from netifaces import interfaces, ifaddresses

app = Flask(__name__)

flask_threaded_default = "1"
flask_debug_default    = "0"
flask_port_default     = "5000"

# they are all set in the first main loop
flask_threaded  = None
flask_debug     = None
flask_port      = None
loadummy_next   = None
loadummy_name   = None

MIME_TEXT = 'text/plain'
MIME_HTML = 'text/html'
MIME_YAML = 'application/x-yaml'
MIME_JSON = 'application/json'


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


def format_answer(req, obj, mimetype=None):
    def format_text(obj):
        return yaml.safe_dump(obj, default_flow_style=False)
    def format_html(obj):
        return \
            "<pre>" + \
            str(escape(yaml.safe_dump(obj, default_flow_style=False))) + \
            "</pre>"
    def format_yaml(obj):
        return yaml.dump(obj, default_flow_style=False)
    if not mimetype:
        accept = request.headers.get('Accept', "")
        mimetype = MIME_TEXT
        if accept == '*/*': mimetype = MIME_TEXT
        elif accept.find('yaml') != -1: mimetype = MIME_YAML
        elif accept.find('json') != -1: mimetype = MIME_JSON
        app.logger.debug("Determined MIME type: {}".format(mimetype))
    else:
        app.logger.debug("Enforced MIME type: {}".format(mimetype))
    handlers = {
        MIME_TEXT : format_text,
        MIME_YAML : format_yaml,
        MIME_HTML : format_html,
        MIME_JSON : json.dumps,
    }
    rsp_data = handlers[mimetype](obj)
    app.logger.debug("Returned data:\n{}".format(rsp_data))
    rsp = make_response(handlers[mimetype](obj))
    rsp.headers['Content-type'] = mimetype
    return rsp


@app.route('/')
def hello_world():
    rv = {}
    rv['hostname']             = socket.gethostname()
    rv['random_uuid']          = uuid_str
    rv['timestamp']            = datetime.datetime.now()
    rv['set_flask_threaded']   = flask_threaded
    rv['set_loadummy_name']    = loadummy_name
    rv['ips']                  = {
        iface: ifaddresses(iface)[2][0]["addr"] for iface in interfaces()
    }

    return format_answer(request, rv)


@app.route('/health')
def health():
    return "OK", 200


@app.route('/pi/<digits>')
def compute_digits(digits):
    digits       = int(digits)

    begin        = time.time()
    pi           = picompute.pi(digits)
    duration     = time.time() - begin

    digits_head  = request.headers.get('Pi-Digits', None)
    pi_str       = str(pi) if not digits_head else str(pi)[-(int(digits_head)):]

    answer       = {
        'duration':  duration,
        'digits':    digits,
        'time':      str(dt.datetime.now()),
        'pi':        pi_str,
    }

    return format_answer(request, answer)


@app.route('/env')
def full_env():
    return format_answer(request, _get_env_vars())


@app.route('/exec', methods=['GET'])
def exec_form():
    return render_template("exec.html"), 200


@app.route('/exec', methods=['POST'])
def exec_exec():
    cmd = request.form['command']
    result = subprocess.check_output(
            cmd + " ; exit 0",
            stderr=subprocess.STDOUT,
            shell=True).decode('utf-8')
    return render_template("pre.html", command=cmd, result=result), 200


@app.route('/env/<start>')
def selected_env(start):
    return format_answer(request, _get_env_vars(start))


@app.route('/request-headers')
def return_headers():
    return format_answer(request, dict(request.headers))


@app.route('/debug/<onoff>')
def debug_enable_disable(onoff):
    if not onoff in ["1", "0"]:
        return format_answer(request, {'error': 'use /debug/1 or /debug/0'})
    onoff = int(onoff)
    msg = ["disabled", "enabled"]
    app.debug = bool(onoff)
    app.logger.debug("You should only see this with debug enabled")
    return format_answer(request, {'message': "debug was {}".format(msg[onoff])})


@app.route('/print', methods=["GET"])
def print_get():
    return render_template("print.html"), 200


@app.route('/print', methods=["POST"])
def print_post():
    print_text = request.form['print']
    print(print_text)
    return redirect("/print")


# will create <num> calls to the backend, with a default digit count of
# <size> plus minus <spread>
@app.route('/distrib/<num>/<size>')
def distribute(num, size):
    def _call(number, url, responseset):
        try:
            r = requests.get(url, headers={'Accept':'json', 'Pi-Digits': '10'})
            res = r.json()
            res['url'] = url
            res['status_code'] = r.status_code
        except Exception as e:
            print(e)
            res = {'url': url, 'status_code': '-1', 'error': str(e)}
        responseset[number] = res
    size   = int(size)
    spread = int(size / 10)
    lower  = int(size - spread/2)
    upper  = int(size + spread/2)
    urls   = [
        loadummy_next+"/pi/{}".format(x) for x in
            random.sample(range(lower, upper), int(num))
    ]
    threads     = []
    i           = 0
    responseset = {}
    begin       = time.time()
    for url in urls:
        t=threading.Thread(name=str(i), target=_call, args=(i,url,responseset))
        threads.append(t)
        t.start()
        i += 1
    for thread in threads:
        thread.join()
    duration    = time.time() - begin
    retval = { 'duration': duration, 'responseset': responseset}
    return format_answer(request, retval)


if __name__ == '__main__':
    uuid_str       = str(uuid.uuid4())
    loadummy_next  = os.environ.get("LOADUMMY_NEXT", False)
    loadummy_name  = os.environ.get("LOADUMMY_NAME", '')
    flask_threaded = os.environ.get('FLASK_THREADED', flask_threaded_default)
    flask_threaded = True if flask_threaded.lower() in ("1", "true", "on") else False
    flask_debug    = os.environ.get('FLASK_DEBUG', flask_debug_default)
    flask_debug    = True if flask_debug.lower() in ("1", "true", "on") else False
    flask_port     = int(os.environ.get('FLASK_PORT', flask_port_default))

    app.run(
        host='0.0.0.0',
        threaded=flask_threaded,
        port=flask_port,
        debug=flask_debug
    )
