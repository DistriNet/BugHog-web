from flask import Blueprint, render_template, make_response
from test_suites.test_suite import TestSuite

iframetest = "iframe.test"

iframe = Blueprint('iframe', __name__, template_folder="templates/iframe")


@iframe.route("/<string:scheme>/<string:suite>/<string:group>/", defaults={'arg': None}, host=iframetest)
@iframe.route("/<string:scheme>/<string:suite>/<string:group>/<string:arg>/", host=iframetest)
def test_suites_iframe(suite, group, scheme, arg):
    return render_template('iframe.html', suite=suite, group=group, scheme=scheme, arg=arg)


@iframe.route("/embed/<string:scheme>/<string:suite_name>/<string:group>/", defaults={'arg': None}, host=iframetest)
@iframe.route("/embed/<string:scheme>/<string:suite_name>/<string:group>/<string:arg>/", host=iframetest)
def test_suites_embed_iframe(suite_name, group, scheme, arg):
    suite = TestSuite.get_suite(suite_name, scheme)
    resp = make_response(suite.render_response(group, arg))
    resp.headers["Content-Security-Policy"] = "default-src 'none'"
    return resp
