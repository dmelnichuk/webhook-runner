import hmac
import json
import os

from bottle import request, response, run

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
        follow = app.config.get('github.follow', 'branch')
        name = app.config.get('github.name', 'master')
        payload = json.loads(body)

        # either 'refs/heads/<name>' or 'refs/tags/<name>'
        if payload['ref'].split('/')[-1] == name:
            deploy(
                name=name,
                base=app.config.get(
                    'github.base',
                    os.path.expanduser('~/www')
                ),
                src=app.config.get('deploy.src', '.'),
            )
    else:
        response.status_code = 401

    return json.dumps({})


run(
    app,
    host=app.config.get('whrunner.host', '127.0.0.1'),
    port=int(app.config.get('whrunner.port', '8080')),
)
