#!/usr/bin/env python3

import datetime as dt
import json
import os
import random
import re
import socket
import subprocess
import sys
import threading
import time
import uuid

import requests
import yaml

import picompute
from gray_conversion import *
from name_generator import get_random_name_pair
from flask import Flask, make_response, redirect, render_template, request
from markupsafe import escape


app = Flask(__name__)

# flask defaults
flask_threaded_default = "1"
flask_debug_default = "0"
flask_port_default = "5000"

# flask values, set in import code
flask_threaded = None
flask_debug = None
flask_port = None
loadummy_next = None
loadummy_name = None

# application values
instance_identifier = " ".join(get_random_name_pair()).lower()
loadummy_next = os.environ.get("LOADUMMY_NEXT", False)
loadummy_name = os.environ.get("LOADUMMY_NAME", "default_name")

# MIME types
MIME_TEXT = "text/plain"
MIME_HTML = "text/html"
MIME_YAML = "application/x-yaml"
MIME_JSON = "application/json"

# colors
fg_color = "black"
bg_color = "white"


def _get_env_vars(var_start=""):
    render = ""
    for key in sorted(os.environ.keys()):
        if not key.startswith(var_start):
            continue
        val = os.environ.get(key)
        addme = escape(("%s = %s" % (key, val)).decode("utf-8"))
        # the "str()" is necessary, otherwise this is (probably) some
        # convenience object which auto-escapes everything you add to it ...
        render += addme + "<br>"
    return render


def format_answer(req, obj, mimetype=None):
    def format_text(obj):
        return yaml.safe_dump(obj, default_flow_style=False)

    def format_html(obj):
        return render_template(
            "pre_simple.html",
            bgcolor=bg_color,
            fgcolor=fg_color,
            content=str(yaml.safe_dump(obj, default_flow_style=False)),
        )

    def format_yaml(obj):
        return yaml.dump(obj, default_flow_style=False)

    if not mimetype:
        accept = request.headers.get("Accept", "")
        mimetype = MIME_HTML
        if accept == "*/*":
            mimetype = MIME_HTML
        elif accept.find("yaml") != -1:
            mimetype = MIME_YAML
        elif accept.find("json") != -1:
            mimetype = MIME_JSON
        app.logger.debug("Determined MIME type: {}".format(mimetype))
    else:
        app.logger.debug("Enforced MIME type: {}".format(mimetype))
    handlers = {
        MIME_TEXT: format_text,
        MIME_YAML: format_yaml,
        MIME_HTML: format_html,
        MIME_JSON: json.dumps,
    }
    rsp_data = handlers[mimetype](obj)
    app.logger.debug("Returned data:\n{}".format(rsp_data))
    rsp = make_response(handlers[mimetype](obj))
    rsp.headers["Content-type"] = mimetype
    return rsp


@app.route("/")
def hello_world():
    rv = {}
    rv["hostname"] = socket.gethostname()
    rv["instance_identifier"] = instance_identifier
    rv["request_identifier"] = str(uuid.uuid4())
    rv["request_timestamp"] = dt.datetime.now()
    rv["set_flask_threaded"] = flask_threaded
    rv["set_loadummy_name"] = loadummy_name
    rv["color_bg"] = bg_color
    rv["color_fg"] = fg_color

    return format_answer(request, rv)


@app.route("/health")
def health():
    return "OK", 200


@app.route("/pi/<digits>")
def compute_digits(digits):
    digits = int(digits)

    begin = time.time()
    pi = picompute.pi(digits)
    duration = time.time() - begin

    digits_head = request.headers.get("Pi-Digits", None)
    pi_str = str(pi) if not digits_head else str(pi)[-(int(digits_head)) :]

    answer = {
        "duration": duration,
        "digits": digits,
        "time": str(dt.datetime.now()),
        "pi": pi_str,
    }

    return format_answer(request, answer)


@app.route("/env")
def full_env():
    return format_answer(request, _get_env_vars())


@app.route("/exec", methods=["GET"])
def exec_form():
    return render_template("exec.html"), 200


@app.route("/exec", methods=["POST"])
def exec_exec():
    cmd = request.form["command"]
    result = subprocess.check_output(
        cmd + " ; exit 0", stderr=subprocess.STDOUT, shell=True
    ).decode("utf-8")
    return render_template("pre.html", command=cmd, result=result), 200


@app.route("/env/<start>")
def selected_env(start):
    return format_answer(request, _get_env_vars(start))


@app.route("/request-headers")
def return_headers():
    return format_answer(request, dict(request.headers))


@app.route("/debug/<onoff>")
def debug_enable_disable(onoff):
    if not onoff in ["1", "0"]:
        return format_answer(request, {"error": "use /debug/1 or /debug/0"})
    onoff = int(onoff)
    msg = ["disabled", "enabled"]
    app.debug = bool(onoff)
    app.logger.debug("You should only see this with debug enabled")
    return format_answer(request, {"message": "debug was {}".format(msg[onoff])})


@app.route("/print", methods=["GET"])
def print_get():
    return render_template("print.html"), 200


@app.route("/print", methods=["POST"])
def print_post():
    print_text = request.form["print"]
    print(print_text, file=sys.stderr)
    return redirect("/print")


# will create <num> calls to the backend, with a default digit count of
# <size> plus minus <spread>
@app.route("/distrib/<num>/<size>")
def distribute(num, size):
    def _call(number, url, responseset):
        try:
            r = requests.get(url, headers={"Accept": "json", "Pi-Digits": "10"})
            res = r.json()
            res["url"] = url
            res["status_code"] = r.status_code
        except Exception as e:
            print(e)
            res = {"url": url, "status_code": "-1", "error": str(e)}
        responseset[number] = res

    size = int(size)
    spread = int(size / 10)
    lower = int(size - spread / 2)
    upper = int(size + spread / 2)
    urls = [
        loadummy_next + "/pi/{}".format(x)
        for x in random.sample(range(lower, upper), int(num))
    ]
    threads = []
    i = 0
    responseset = {}
    begin = time.time()
    for url in urls:
        t = threading.Thread(name=str(i), target=_call, args=(i, url, responseset))
        threads.append(t)
        t.start()
        i += 1
    for thread in threads:
        thread.join()
    duration = time.time() - begin
    retval = {"duration": duration, "responseset": responseset}
    return format_answer(request, retval)


if __name__ == "__main__":
    flask_threaded = os.environ.get("FLASK_THREADED", flask_threaded_default)
    flask_threaded = True if flask_threaded.lower() in ("1", "true", "on") else False
    flask_debug = os.environ.get("FLASK_DEBUG", flask_debug_default)
    flask_debug = True if flask_debug.lower() in ("1", "true", "on") else False
    flask_port = int(os.environ.get("FLASK_PORT", flask_port_default))

    startup_time = float(os.environ.get("STARTUP_TIME", "0"))

    random.seed()

    bg_color = os.environ.get("COLOR", "dddddd")
    if bg_color == "random":
        bg_color, bg_color_hex = random.choice(list(html_colors.items()))
    elif re.match("[0-9a-f]{6}", bg_color):
        bg_color_hex = bg_color
    else:
        bg_color_hex = get_color_hex_value(bg_color)
        if bg_color_hex is None:
            print(f"\nWARNING: Unknown color: '{bg_color}'\n")
            bg_color = "white"
            bg_color_hex = "ffffff"
    gray_value = get_gray_value(bg_color_hex)
    fg_color = "333333" if gray_value >= 0.5 else "eeeeee"

    print(f"=====================STARTUP==========================")
    print(f"using bg_color:         {bg_color}")
    print(f"using fg_color:         {fg_color}")
    print(f"using startup_time:     {startup_time}")
    print(f"using flask_port:       {flask_port}")
    print(f"using flask_threaded:   {flask_threaded}")
    print(f"using flask_debug:      {flask_debug}")
    print(f"======================================================")
    print()

    print(f"Starting up for {startup_time} seconds ... ", end="", flush=True)
    print()

    time.sleep(startup_time)
    print("done.")
    app.run(host="0.0.0.0", threaded=flask_threaded, port=flask_port, debug=flask_debug)
