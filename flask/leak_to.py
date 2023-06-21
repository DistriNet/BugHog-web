import datetime
import json
import os
from urllib.parse import urlparse

import requests
from requests.exceptions import ConnectionError
from custom_test_cases import test_cases
from test_suites.test_suite import TestSuite

from flask import (Blueprint, escape, make_response, render_template, request,
                   send_file)

aditioncom = "adition.com"
subaditioncom = "sub.adition.com"
subsubaditioncom = "sub.sub.adition.com"

leak_to = Blueprint('leak_to', __name__, template_folder='templates/leak_to')


@leak_to.route('/', host=aditioncom)
@leak_to.route('/', host=subaditioncom)
@leak_to.route('/', host=subsubaditioncom)
def index():
    return f"Requests are leaked to this website : {request.scheme}"


@leak_to.route('/sw.js', host=aditioncom)
def custom_sw():
    sw_script = request.args.get('script')
    return sw_script, 200, {"Content-Type": "text/javascript"}


@leak_to.route('/set_cookies/', host=aditioncom)
def set_cookies():
    cookie_exp_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
    resp = make_response(render_template('set_cookies.html', title='Index'))
    resp.set_cookie("generic", "1", expires=cookie_exp_date)
    resp.set_cookie("secure", "1", expires=cookie_exp_date, secure=True)
    resp.set_cookie("httpOnly", "1", expires=cookie_exp_date, httponly=True)
    resp.set_cookie("lax", "1", expires=cookie_exp_date, samesite='lax')
    resp.set_cookie("strict", "1", expires=cookie_exp_date, samesite='strict')
    return resp


@leak_to.route('/report/', methods=["GET", "POST"], host=aditioncom)
def report_leak():
    leak = request.args.get('leak')
    if leak is not None:
        if leak == "link-prerender":
            return render_template('prerender.html')
        resp = make_response(render_template("set_cookies.html", title="Report", to_report=leak))
    else:
        resp = make_response(render_template("set_cookies.html", title="Report", to_report="Nothing to report"))

    cookie_exp_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
    resp.set_cookie("generic", "1", expires=cookie_exp_date)
    resp.set_cookie("secure", "1", expires=cookie_exp_date, secure=True)
    resp.set_cookie("httpOnly", "1", expires=cookie_exp_date, httponly=True)
    resp.set_cookie("lax", "1", expires=cookie_exp_date, samesite='lax')
    resp.set_cookie("strict", "1", expires=cookie_exp_date, samesite='strict')

    # Respond to collector on same IP
    remote_ip = request.remote_addr

    response_data = {
        'url': request.url,
        'method': request.method,
        'headers': dict(request.headers),
        'content': request.data.decode('utf-8')
    }
    try:
        requests.post(
            f"http://{remote_ip}:5001/report/",
            json=response_data
        )
    except ConnectionError:
        print(f'WARNING: Could not propagate request to collector at {remote_ip}:5000')

    return resp


@leak_to.route('/report/if/using/<string:protocol>', host=aditioncom)
def report_leak_if_using_http(protocol):
    """
    Forces request to /report/?leak=xxx if a request was received over a certain protocol.
    """
    leak = request.args.get('leak')
    if request.url.startswith(f"{protocol}://"):
        return "Redirect", 307, {"Location": f"https://adition.com/report/?leak={leak}"}
    else:
        return f"Request was not received over {protocol}", 200, {}


@leak_to.route('/report/if/<string:expected_header_name>', host=aditioncom)
def report_leak_if_present(expected_header_name: str):
    """
    Forces request to /report/?leak=xxx if a request header by name of expected_header_name was received.
    """
    if expected_header_name not in request.headers:
        return f"Header {expected_header_name} not found", 200, {"Allow-CSP-From": "*"}

    leak = request.args.get('leak')
    if leak is not None:
        return "Redirect", 307, {"Location": f"https://adition.com/report/?leak={leak}", "Allow-CSP-From": "*"}
    else:
        return "Redirect", 307, {"Location": "https://adition.com/report/", "Allow-CSP-From": "*"}


@leak_to.route('/report/if/<string:expected_header_name>/contains/<string:expected_header_value>', host=aditioncom)
def report_leak_if_contains(expected_header_name: str, expected_header_value: str):
    """
    Forces request to /report/?leak=xxx if a request header by name of expected_header_name with value expected_header_value was received.
    """
    if expected_header_name not in request.headers:
        return f"Header {expected_header_name} not found", 200, {"Allow-CSP-From": "*"}
    elif expected_header_value not in request.headers[expected_header_name]:
        return f"Header {expected_header_name} found, but expected value '{expected_header_value}' did not equal real value '{request.headers[expected_header_name]}'", 200, {"Allow-CSP-From": "*"}

    leak = request.args.get('leak')
    if leak is not None:
        return "Redirect", 307, {"Location": f"https://adition.com/report/?leak={leak}", "Allow-CSP-From": "*"}
    else:
        return "Redirect", 307, {"Location": "https://adition.com/report/", "Allow-CSP-From": "*"}


@leak_to.route("/embed/prerender/test/<string:scheme>/<string:group>/", defaults={'arg': None}, host=aditioncom)
@leak_to.route('/embed/prerender/test/<string:scheme>/<string:group>/<string:arg>', host=aditioncom)
def embed_prerender_test(scheme, group, arg):
    suite = TestSuite.get_suite("basic", scheme)
    return suite.render_response(group, arg)


'''
Custom test cases
'''


@leak_to.route("/resources/<path:path>", host=aditioncom)
def resources(path):
    file_path = os.path.join("/app/static/", path)
    if not os.path.isfile(file_path):
        return "Resource not found", 404
    if path.endswith(".swf"):
        response = make_response(send_file(file_path))
        response.headers["Content-Type"] = "application/x-shockwave-flash"
        return response
    return send_file(file_path)


@leak_to.route("/custom/<string:folder1>/<string:folder2>", host=aditioncom)
@leak_to.route("/custom/<string:folder1>/<string:folder2>", host=subaditioncom)
@leak_to.route("/custom/<string:folder1>/<string:folder2>", host=subsubaditioncom)
def custom_test_cases(folder1, folder2):
    host = urlparse(request.base_url).hostname
    path = os.path.join(folder1, folder2)

    test_cases_str = escape(json.dumps(test_cases, indent=4))
    if test_cases is None:
        return "Could not load any test cases", 404
    if host not in test_cases:
        return f"Could not find domain '{host}'<br>Test cases:<br>{test_cases_str}", 404
    if path not in test_cases[host]:
        return f"Could not find path '{path}' for domain '{host}'<br>Test cases:<br>{test_cases_str}", 404

    content = test_cases[host][path]["content"]
    status = 200  # Default value
    # resp = make_response(render_template("custom", content=content))
    headers = dict()
    if "headers" in test_cases[host][path]:
        for header in test_cases[host][path]["headers"]:
            if header["key"] == "status":
                status = header["value"]
            else:
                if header["key"] not in headers.keys():
                    headers[header["key"]] = list()
                headers[header["key"]].append(header["value"])
    # resp.headers = headers
    return content, status, headers
