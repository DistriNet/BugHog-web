import os
import json
from test_suites.test_suite import TestSuite
from flask import render_template, make_response, Blueprint, request, escape, send_file
from custom_test_cases import test_cases

leaktest = "leak.test"
leaktest_sub = "sub.leak.test"

leak_from = Blueprint('leak_from', __name__, template_folder="templates/leak_from")


@leak_from.route("/", host=leaktest)
def index():
    return "Requests are leaked from this domain"


@leak_from.route("/<string:scheme>/<string:suite_name>/<string:group>/", defaults={'arg': None}, host=leaktest)
@leak_from.route("/<string:scheme>/<string:suite_name>/<string:group>/<string:arg>/", host=leaktest)
def test_suites(suite_name, group, scheme, arg):
    suite = TestSuite.get_suite(suite_name, scheme, suite_args=request.args)
    return suite.render_response(group, arg)


@leak_from.route("/<string:encoded_base_url>/ac.appcache", host=leaktest)
def appcache_manifest(encoded_base_url):
    resp = make_response(render_template('appcache/ac.appcache', base_url=TestSuite.decode_base_url(encoded_base_url)))
    resp.headers["Content-Type"] = "text/cache-manifest"
    return resp


@leak_from.route("/<string:scheme>/<string:suite_name>/script.js", host=leaktest)
def js_script(scheme, suite_name):
    suite_args = request.args
    suite = TestSuite.get_suite(suite_name, scheme, suite_args)
    return suite.js_script()


@leak_from.route("/<string:scheme>/<string:suite_name>/sw.js", host=leaktest)
def sw_script(scheme, suite_name):
    suite_args = request.args
    suite = TestSuite.get_suite(suite_name, scheme, suite_args)
    return suite.sw_script()


@leak_from.route("/<string:scheme>/<string:suite_name>/sw_init.js", host=leaktest)
def sw_init_script(scheme, suite_name):
    suite_args = request.args
    suite = TestSuite.get_suite(suite_name, scheme, suite_args)
    return suite.sw_init_script()


@leak_from.route("/<string:scheme>/<string:suite_name>/css.css", host=leaktest)
def css(scheme, suite_name):
    suite_args = request.args
    suite = TestSuite.get_suite(suite_name, scheme, suite_args)
    return suite.css()

@leak_from.route("/<string:scheme>/<string:suite_name>/css.css", host=leaktest)
def css_added(scheme, suite_name):
    suite_args = request.args
    suite = TestSuite.get_suite(suite_name, scheme, suite_args)
    return suite.css_added()


@leak_from.route("/<string:scheme>/<string:suite_name>/pdf/<string:manner>/", host=leaktest)
def pdf(scheme, suite_name, manner):
    suite_args = request.args
    suite = TestSuite.get_suite(suite_name, scheme, suite_args)
    if manner == "iframe":
        return suite.pdf_iframe()
    elif manner == "redirect":
        return suite.pdf_redirect()
    else:
        raise NotImplementedError("Manner '%s' not supported" % manner)


'''
Feature policy
'''

@leak_from.route("/<string:scheme>/feature-policy/<string:directive>/<string:mechanism>", host=leaktest)
@leak_from.route("/<string:scheme>/feature-policy/<string:directive>/<string:mechanism>", host=leaktest_sub)
def feature_policy(scheme, directive, mechanism):
    policy = request.args.get("policy")
    resp = make_response(render_template("feature_policy/%s.html" % directive, scheme=scheme, mechanism=mechanism))
    resp.headers["Feature-Policy"] = policy
    return resp


'''
Embedded tests
'''

@leak_from.route("/embed/prerender/<string:scheme>/<string:suite_name>/<string:group>/", defaults={'arg': None}, host=leaktest)
@leak_from.route('/embed/prerender/<string:scheme>/<string:suite_name>/<string:group>/<string:arg>', host=leaktest)
def embed_prerender(scheme, suite_name, group, arg):
    return render_template("embed/prerender.html", scheme=scheme, suite_name=suite_name, group=group, arg=arg)


@leak_from.route("/embed/iframe/<string:scheme>/<string:suite_name>/<string:group>/", defaults={'arg': None}, host=leaktest)
@leak_from.route('/embed/iframe/<string:scheme>/<string:suite_name>/<string:group>/<string:arg>', host=leaktest)
def embed_iframe(scheme, suite_name, group, arg):
    resp = make_response(render_template("embed/iframe.html", suite_name=suite_name, scheme=scheme, group=group, arg=arg))
    resp.headers["Content-Security-Policy"] = "default-src 'self'"
    return resp


@leak_from.route("/embed/iframe2/<string:scheme>/<string:suite_name>/<string:group>/", defaults={'arg': None}, host=leaktest)
@leak_from.route('/embed/iframe2/<string:scheme>/<string:suite_name>/<string:group>/<string:arg>', host=leaktest)
def embed_iframe2(scheme, suite_name, group, arg):
    resp = make_response(render_template("embed/iframe_other_origin.html", suite_name=suite_name, scheme=scheme, group=group, arg=arg))
    #resp.headers["Content-Security-Policy"] = "default-src 'self'"
    return resp


'''
Methods solely used for manual experiments
'''

@leak_from.route("/exp/iframe_local_pdf/", host=leaktest)
def iframe_local_pdf():
    resp = make_response("<embed src='file:///Users/gertjanfranken/Downloads/Fahrenheit_451.pdf'></embed> <link rel='prerender' src='//file:///Users/gertjanfranken/Downloads/Fahrenheit_451.pdf'>")
    resp.headers["Location"] = "//file:///Users/gertjanfranken/Downloads/Fahrenheit_451.pdf"
    resp.status = "300"
    return resp


@leak_from.errorhandler(500)
def internal_server_error(e):
    return render_template("error_500.html", exception=e)


'''
Custom test cases
'''


@leak_from.route("/resources/<path:path>", host=leaktest)
def resources(path):
    file_path = os.path.join("/app/static/", path)
    if not os.path.isfile(file_path):
        return "Resource not found", 404
    if path.endswith(".swf"):
        response = make_response(send_file(file_path))
        response.headers["Content-Type"] = "application/x-shockwave-flash"
        return response
    return send_file(file_path)


@leak_from.route("/custom/<string:folder1>/<string:folder2>", host=leaktest)
def custom_test_cases(folder1, folder2):
    path = os.path.join(folder1, folder2)

    test_cases_str = escape(json.dumps(test_cases, indent=4))
    if test_cases is None:
        return "Could not load any test cases", 404
    if "leak.test" not in test_cases:
        return f"Could not find domain '{leaktest}'<br>Test cases:<br>{test_cases_str}", 404
    if path not in test_cases["leak.test"]:
        return f"Could not find path '{path}' for domain '{leaktest}'<br>Test cases:<br>{test_cases_str}", 404

    content = test_cases["leak.test"][path]["content"]
    status = 200 # Default value
    #resp = make_response(render_template("custom", content=content))
    headers = dict()
    if "headers" in test_cases["leak.test"][path]:
        for header in test_cases["leak.test"][path]["headers"]:
            if header["key"] == "status":
                status = header["value"]
            else:
                if header["key"] not in headers.keys():
                    headers[header["key"]] = list()
                headers[header["key"]].append(header["value"])
    #resp.headers = headers
    return content, status, headers
