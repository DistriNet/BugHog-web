import base64
from abc import abstractmethod
from flask import render_template, make_response, request, send_from_directory

class TestSuite:

    path = "report"

    def __init__(self, dst_scheme, suite_args, policy=None):
        self.dst_scheme = dst_scheme
        self.suite_args = suite_args
        self.policy = policy


    @staticmethod
    def get_suite(name, dst_scheme, suite_args=None):
        if name == "basic":
            return BasicSuite(dst_scheme, suite_args)
        elif name == "csp":
            return CSPSuite(dst_scheme, suite_args)
        elif name == "referrer-policy":
            return ReferrerPolicySuite(dst_scheme, suite_args)
        elif name == "hsts":
            return HSTSSuite(dst_scheme, suite_args)
        else:
            raise AttributeError(f'Could not find evaluation suite \'{name}\'')


    def render_response(self, group, test_arg):
        if group == "static":
            iframe_js_atob = base64.b64encode(('<img src="%s">' % self.full_url('iframe-javascript-src-3')).encode("utf-8"))
            svg_via_data = self.full_url('svg-via-data').replace('h', '%68', 1).replace('/', '%2f', 1)
            return make_response(render_template('static/static.html', title=group, scheme=self.dst_scheme, base_url=self.base_url(), iframe_js_atob=iframe_js_atob, svg_via_data=svg_via_data, suite_name=self.name, policy=self.policy))
        if group == "static_added":
            return make_response(render_template('static_added/static.html', title=group, scheme=self.dst_scheme, base_url=self.base_url(), suite_name=self.name, policy=self.policy))
        elif group == "appcache":
            return make_response(render_template('appcache/appcache.html', title=group, scheme=self.dst_scheme, host=request.host, encoded_base_url=self.encode_base_url()))
        elif group == "redirect":
            if "location-header" in test_arg:
                resp = make_response(render_template('redirect.html', title=group, scheme=self.dst_scheme))
                resp.headers["Location"] = self.full_url(test_arg)
                resp.status = test_arg[-3:]
                return resp
            elif "refresh-header" in test_arg:
                resp = make_response(render_template('redirect.html', title=group, scheme=self.dst_scheme))
                resp.headers["Refresh"] = "0; url=%s" % self.full_url(test_arg)
                return resp
            else:
                return make_response(render_template('redirect.html', title=group, type=test_arg, url=self.full_url(test_arg)))
        elif group == "header-csp":
            resp = make_response(render_template('header-csp.html', title=group, scheme=self.dst_scheme))
            self.csp_headers(test_arg, resp)
            return resp
        elif group == "header-link":
            resp = make_response(render_template('header-link.html', title=group, scheme=self.dst_scheme))
            resp.headers["Link"] = base64.b64decode(test_arg)
            return resp
        elif group == "pdf":
            if self.name == "hsts":
                return make_response(render_template('pdf.html', title=group, scheme=self.dst_scheme, suite_name=self.name, policy=self.policy))
            else:
                return make_response(render_template('pdf.html', title=group, scheme=self.dst_scheme, suite_name=self.name, policy=self.policy))
        elif group == "script":
            return make_response(render_template('script/script.html', title=group, scheme=self.dst_scheme, suite_name=self.name, policy=self.policy))
        elif group == "script_inline":
            return make_response(render_template('script/script_inline.html', title=group, scheme=self.dst_scheme))
        elif group == "sw":
            return make_response(render_template('sw/sw.html', title=group, scheme=self.dst_scheme, suite_name=self.name, group=group, policy=self.policy))
        else:
            return make_response("Unknown group: %s" % group)


    def csp_headers(self, leak, resp):
        if leak == "csp-report-uri":
            resp.headers["Content-Security-Policy"] = "default-src 'none'; report-uri %s" % self.full_url(leak)
        elif leak == "csp-report-uri-2":
            resp.headers["Content-Security-Policy-Report-Only"] = "default-src 'none'; report-uri %s" % self.full_url(leak)
        elif leak == "csp-report-to":
            resp.headers["Report-To"] = '{ "url": "%s","group": "endpoint-1","max-age": 10886400 }' % self.full_url(leak)
            resp.headers["Content-Security-Policy"] = "script-src 'self'; report-to=endpoint-1"
        elif leak == "x-csp-report-uri":
            resp.headers["X-Content-Security-Policy"] = "default-src 'none'; report-uri %s" % self.full_url(leak)
        elif leak == "x-csp-report-uri-2":
            resp.headers["X-Content-Security-Policy-Report-Only"] = "default-src 'none'; report-uri %s" % self.full_url(leak)
        elif leak == "x-csp-report-to":
            resp.headers["Report-To"] = '{ "url": "%s","group": "endpoint-2","max-age": 10886400 }' % self.full_url(leak)
            resp.headers["X-Content-Security-Policy"] = "default-src 'none'; report-to=endpoint-2"
        elif leak == "x-webkit-csp-report-uri":
            resp.headers["X-Webkit-CSP"] = "default-src 'none'; report-uri %s" % self.full_url(leak)
        elif leak == "nel-report":
            resp.headers["Report-To"] = '{"group": "network-errors", "max_age": 2592000, "endpoints": [{"url": "%s"}]}' % self.full_url(leak)
            resp.headers["NEL"] = '{"report_to": "network-errors", "max_age": 2592000, "include_subdomains": true, "success_fraction": 1.0}'
        else:
            raise NotImplementedError("Unknown type: %s" % leak)


    def pdf_iframe(self):
        return make_response(send_from_directory('static', filename='pdf/%s-iframe.pdf' % self.dst_scheme))


    def pdf_redirect(self):
        return make_response(send_from_directory('static', filename='pdf/%s-redirect.pdf' % self.dst_scheme))


    def css(self):
        resp = make_response(render_template('static/css.css', base_url=self.base_url()))
        resp.headers["Content-Type"] = "text/css"
        return resp

    def css_added(self):
        resp = make_response(render_template('static_added/css.css', base_url=self.base_url()))
        resp.headers["Content-Type"] = "text/css"
        return resp


    def js_script(self):
        return render_template('script/script.js', base_url=self.base_url(), base_url_websocket=self.base_url_websocket(), policy=self.policy)


    def sw_script(self):
        resp = make_response(render_template('sw/sw.js', base_url=self.base_url(), base_url_websocket=self.base_url_websocket()))
        resp.headers["Content-Type"] = "application/javascript"
        return resp


    def sw_init_script(self):
        resp = make_response(render_template('sw/sw_init.js', scheme=self.dst_scheme, suite_name=self.name, policy=self.policy))
        resp.headers["Content-Type"] = "application/javascript"
        return resp


    @property
    @abstractmethod
    def name(self):
        pass


    @property
    @abstractmethod
    def dst_domain(self):
        pass


    def base_url(self):
        return "%s://%s/%s/" % (self.dst_scheme, self.dst_domain, self.path)


    def base_url_websocket(self):
        if self.dst_scheme == "http":
            return "%s://%s/%s/" % ("ws", self.dst_domain, self.path)
        elif self.dst_scheme == "https":
            return "%s://%s/%s/" % ("wss", self.dst_domain, self.path)
        else:
            raise NotImplementedError("No conversion to ws for '%s'" % self.dst_scheme)


    def full_url(self, leak):
        return "%s?leak=%s" % (self.base_url(), leak)


    def encode_base_url(self):
        return base64.b64encode(self.base_url().encode("utf-8"))


    @staticmethod
    def decode_base_url(url):
        return base64.b64decode(url).decode("utf-8")


class BasicSuite(TestSuite):

    name = "basic"
    dst_domain = "adition.com"

    def __init__(self, dst_scheme, suite_args):
        TestSuite.__init__(self, dst_scheme, suite_args)


class CSPSuite(TestSuite):

    name = "csp"
    dst_domain = "adition.com"

    def __init__(self, dst_scheme, suite_args):
        if suite_args is not None and "policy" in suite_args:
            policy = suite_args["policy"]
        else:
            policy = "default-src 'self'"
        TestSuite.__init__(self, dst_scheme, suite_args, policy)


    def render_response(self, group, test_arg):
        resp = super().render_response(group, test_arg)
        resp.headers["Content-Security-Policy"] = self.policy
        return resp


    def css(self):
        resp = super().css()
        resp.headers["Content-Security-Policy"] = self.policy
        return resp


    def sw_script(self):
        resp = super().sw_script()
        resp.headers["Content-Security-Policy"] = self.policy
        return resp


    def sw_init_script(self):
        resp = super().sw_script()
        resp.headers["Content-Security-Policy"] = self.policy
        return resp


class ReferrerPolicySuite(TestSuite):

    name = "referrer-policy"
    dst_domain = "adition.com"

    def __init__(self, dst_scheme, suite_args):
        if suite_args is not None and "policy" in suite_args:
            policy = suite_args["policy"]
        else:
            policy = "no-referrer"
        TestSuite.__init__(self, dst_scheme, suite_args, policy)


    def render_response(self, group, test_arg):
        resp = super().render_response(group, test_arg)
        resp.headers["Referrer-Policy"] = self.policy
        return resp


    def css(self):
        resp = super().css()
        resp.headers["Referrer-Policy"] = self.policy
        return resp


    def sw_script(self):
        resp = TestSuite.sw_script()
        resp.headers["Referrer-Policy"] = self.policy
        return resp


class HSTSSuite(TestSuite):

    name = "hsts"
    dst_domain = ""

    def __init__(self, dst_scheme, suite_args):
        if suite_args is not None and "policy" in suite_args:
            policy = suite_args["policy"]
            if "includeSubDomains" in policy:
                self.dst_domain = "sub.hsts-only.com"
            else:
                self.dst_domain = "hsts-only.com"
        else:
            policy = "max-age=31536000"
            self.dst_domain = "hsts-only.com"
        TestSuite.__init__(self, dst_scheme, suite_args, policy)


    def pdf_iframe(self):
        if "includeSubDomains" in self.policy:
            return make_response(send_from_directory('static', filename='pdf/hsts-sub-%s-iframe.pdf' % self.dst_scheme))
        else:
            return make_response(send_from_directory('static', filename='pdf/hsts-%s-iframe.pdf' % self.dst_scheme))


    def pdf_redirect(self):
        if "includeSubDomains" in self.policy:
            return make_response(send_from_directory('static', filename='pdf/hsts-sub-%s-redirect.pdf' % self.dst_scheme))
        else:
            return make_response(send_from_directory('static', filename='pdf/hsts-%s-redirect.pdf' % self.dst_scheme))
