import hmac
import json

from bottle import request, response, run
from invoke.context import Context

from config import app
from tasks import deploy


@app.route('/webhook/', method='POST')
def webhook():
    body = request._get_body_string()

    # check signature
    signature = request.headers.get('X-Hub-Signature')
    sha, signature = signature.split('=')
    secret = str.encode(app.config.get('github.secret'))
    digest = hmac.new(secret, body, digestmod='sha1').hexdigest()
    if hmac.compare_digest(digest, signature):
        # check branch or tag
        name = app.config.get('github.name', 'master')
        payload = json.loads(body.decode('utf-8'))

        # either 'refs/heads/<name>' or 'refs/tags/<name>'
        if payload['ref'].split('/')[-1] == name:
            ctx = Context()
            ctx.config.update(app.config)
            deploy(ctx)
    else:
        response.status_code = 401

    return json.dumps({})


run(
    app,
    host=app.config.get('whrunner.host', '127.0.0.1'),
    port=int(app.config.get('whrunner.port', '8080')),
)
