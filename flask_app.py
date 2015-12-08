from flask import Flask, request, make_response, render_template
from jinja2 import escape
import requests, picompute, time, os, socket, uuid, datetime, yaml, random, json, threading, subprocess
import datetime as dt

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


def format_answer(req, obj):
    def format_text(obj):
        return \
            "<pre>" + \
            str(escape(yaml.safe_dump(obj, default_flow_style=False))) + \
            "</pre>"
    def format_yaml(obj):
        return yaml.dump(obj, default_flow_style=False)
    accept = request.headers.get('Accept')
    mimetype = 'text/html'
    if accept.find('yaml') != -1: mimetype = 'application/x-yaml'
    if accept.find('json') != -1: mimetype = 'application/json'
    handlers = {
        'application/x-yaml' : format_yaml,
        'application/json'   : json.dumps,
        'text/html'          : format_text
    }
    rsp = make_response(handlers[mimetype](obj))
    rsp.headers['Content-type'] = mimetype
    return rsp


@app.route('/')
def hello_world():
    rv = {}
    rv['hostname']             = socket.gethostname()
    rv['ip']                   = _get_host_ip()
    rv['random_uuid']          = uuid_str
    rv['timestamp']            = datetime.datetime.now()
    rv['set_flask_threaded']   = flask_threaded
    rv['set_loadummy_name']    = loadummy_name

    return format_answer(request, rv)


@app.route('/pi/<digits>')
def compute_digits(digits):
    digits       = int(digits)

    begin        = time.time()
    pi           = picompute.pi(digits)
    duration     = time.time() - begin

    answer              = {}
    answer['duration']  = duration
    answer['digits']    = digits
    answer['time']      = str(dt.datetime.now())
    answer['pi']        = str(pi)

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


# will create <num> calls to the backend, with a default digit count of
# <size> plus minus <spread>
@app.route('/distrib/<num>/<size>')
def distribute(num, size):
    def _call(number, url, responseset):
        try:
            r = requests.get(url, headers={'Accept':'json'})
            res = r.json()
            res['url'] = url
            res['status_code'] = r.status_code
        except Exception as e:
            print(e)
            res = { 'url': url, 'status_code': '-1' }
        responseset[number] = res
    size   = int(size)
    spread = int(size / 10)
    lower  = int(size - spread/2)
    upper  = int(size + spread/2)
    urls   = [
        loadummy_next+"/pi/{}".format(x) for x in
            [random.randint(lower, upper) for x in range(int(num))]
    ]
    threads     = []
    i           = 0
    responseset = {}
    for url in urls:
        t=threading.Thread(name=str(i), target=_call, args=(i,url,responseset))
        threads.append(t)
        t.start()
        i += 1
    for thread in threads:
        thread.join()

    return format_answer(request, responseset)


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
