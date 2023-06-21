from flask import Flask
from leak_from import leak_from
from leak_to import leak_to
from hsts_only import hsts_only
from iframe import iframe
from demo import demo
from custom_test_cases import load_custom_test_cases


app = Flask(__name__, host_matching=True, static_host="leak.test")
app.url_map.strict_slashes = False
app.register_blueprint(leak_from)
app.register_blueprint(leak_to)
app.register_blueprint(hsts_only)
app.register_blueprint(iframe)
app.register_blueprint(demo)
load_custom_test_cases("/custom_pages")

if __name__ == "__main__":
    #app.config["SERVER_NAME"] = "leak.test"
    context = ('ssl/leak.crt', 'ssl/leak.key')
    app = Flask(__name__, host_matching=True, static_host="leak.test:5000")
    app.url_map.strict_slashes = False
    app.register_blueprint(leak_from)
    app.register_blueprint(leak_to)
    app.register_blueprint(hsts_only)
    app.register_blueprint(iframe)
    app.register_blueprint(demo)
    app.run(host='127.0.0.1', ssl_context=context)
    load_custom_test_cases("/custom_pages")
