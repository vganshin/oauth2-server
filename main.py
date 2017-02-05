import flask
import json
from functools import wraps
from flask import request, Response


app = flask.Flask(__name__)


def dump_json(message):
    try:
        return json.dumps(json.loads(message.decode('utf-8')), indent=2)
    except Exception:
        return message.decode('utf-8')


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == 'admin' and password == '1234'


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)

    return decorated


def resp(code, data):
    return flask.Response(
        status=code,
        mimetype="application/json",
        response=json.dumps(data)
    )


# e.g. failed to parse json
@app.errorhandler(400)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(404)
def page_not_found(e):
    return resp(400, {})


@app.errorhandler(401)
def not_auth(e):
    return resp(401, {})

data = []


def to_data(url, message):
    from datetime import datetime
    return dict(
        datetime=str(datetime.now()),
        url=url,
        message=message
    )


def data_to_html():
    from functools import reduce
    return reduce(
        lambda a, b: a + b,
        map(
            lambda param: '<p>{datetime} <b>{url}</b></p><pre>{message}</pre><hr>'.format(**param),
            data
        ),
        "<hr>"
    )


def to_html(data):
    return '<p>{datetime} <b>{url}</b></p><pre>{message}</pre><hr>'.format(**data)


@app.route('/clear', methods=['POST'])
def clear():
    with open('data.txt', 'w') as f:
        f.write("<h3>History</h3><hr>")
    return flask.Response(status=200, response="File deleted")


@app.route('/history', methods=['GET'])
def history():
    return flask.Response(status=200, response=open('data.txt', 'r').read())


@app.route('/none', methods=['POST'])
def none():
    with open('data.txt', 'a') as f:
        f.write(to_html(to_data('/none', dump_json(request.data))))
    return flask.Response(status=200, response="")


@app.route('/basic', methods=['POST'])
@requires_auth
def basic():
    with open('data.txt', 'a') as f:
        f.write(to_html(to_data('/basic', dump_json(request.data))))
    return flask.Response(status=200, response="")


@app.route('/oauth2', methods=['POST'])
def oauth2():
    if not request.headers.get('Authorization') or "Bearer" != request.headers.get('Authorization')[:6]:
        return flask.Response(status=401, response="Not Auth")
    with open('data.txt', 'a') as f:
        f.write(to_html(to_data('/oauth2', dump_json(request.data))))
    return flask.Response(status=200, response="")


if __name__ == '__main__':
    # app.debug = True
    app.run(host="0.0.0.0")
