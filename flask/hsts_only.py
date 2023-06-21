import datetime
from flask import Blueprint, render_template, make_response, request
from test_suites.test_suite import TestSuite

hsts_onlycom = "hsts-only.com"
sub_hsts_onlycom = "sub.hsts-only.com"

hsts_only = Blueprint('hsts_only', __name__, template_folder='templates/leak_to')


@hsts_only.route('/', host=hsts_onlycom)
def index():
    return "Requests are leaked to this website : %s" % request.scheme


@hsts_only.route('/set_cookies/', host=hsts_onlycom)
def set_headers():
    policy = request.args.get("policy")
    resp = make_response(render_template('set_cookies.html', title='Index'))
    resp.headers["Strict-Transport-Security"] = policy
    set_cookies(resp)
    return resp


def set_cookies(resp):
    cookie_exp_date = datetime.datetime.now() + datetime.timedelta(weeks=4)
    resp.set_cookie("generic", "1", expires=cookie_exp_date)
    resp.set_cookie("secure", "1", expires=cookie_exp_date, secure=True)
    resp.set_cookie("httpOnly", "1", expires=cookie_exp_date, httponly=True)
    resp.set_cookie("lax", "1", expires=cookie_exp_date, samesite='lax')
    resp.set_cookie("strict", "1", expires=cookie_exp_date, samesite='strict')


@hsts_only.route('/report/', host=hsts_onlycom)
@hsts_only.route('/report/', host=sub_hsts_onlycom)
def report_leak():
    leak = request.args.get('leak')
    if leak is not None:
        if leak == "link-prerender":
            return render_template('prerender.html')
        return "Report: %s" % leak
    else:
        return "Nothing to report"


@hsts_only.route("/embed/prerender/test/<string:scheme>/<string:group>/", defaults={'arg': None}, host=hsts_onlycom)
@hsts_only.route('/embed/prerender/test/<string:scheme>/<string:group>/<string:arg>', host=hsts_onlycom)
def embed_prerender_test(scheme, group, arg):
    suite = TestSuite.get_suite("basic", scheme)
    return suite.render_response(group, arg)
