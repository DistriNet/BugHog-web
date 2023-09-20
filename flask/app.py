from flask import Flask
from experiments import exp_bp


app = Flask(__name__)
app.register_blueprint(exp_bp)

if __name__ == "__main__":
    context = ('ssl/leak.crt', 'ssl/leak.key')
    app = Flask(__name__)
    app.register_blueprint(exp_bp)
    app.run(host='127.0.0.1', ssl_context=context)
