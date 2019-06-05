import hmac
import json
import logging
from threading import Thread

from bottle import request, response, run
from invoke.context import Context

from config import app
from tasks import deploy


logger = logging.Logger(name=__name__)


@app.route('/webhook/', method='POST')
def webhook():
    logger.info('Delivery is started.')
    body = request._get_body_string()

    # check signature
    # set defaults to prevent giving out 500
    signature = request.headers.get('X-Hub-Signature', '=')
    sha, signature = signature.split('=')
    secret = str.encode(app.config.get('github.secret', ''))
    digest = hmac.new(secret, body, digestmod='sha1').hexdigest()
    if hmac.compare_digest(digest, signature):
        # check branch or tag
        name = app.config.get('github.name', 'master')
        payload = json.loads(body.decode('utf-8'))
        logger.info('Delivery ID={}'.format(
            request.headers.get('X-GitHub-Delivery', 'Unknown'))
        )
        # either 'refs/heads/<name>' or 'refs/tags/<name>'
        pushed_name = payload['ref'].split('/')[-1]
        logger.info('Name of a branch or a tag being pushed: {}'.format(
            pushed_name
        ))
        if pushed_name == name:
            ctx = Context()
            ctx.config.update(app.config)
            Thread(target=deploy, args=(ctx, )).start()
        else:
            logger.info('Skipping delivery.')
    else:
        response.status = 401
        logger.error('Delivery was not authorized.')

    return json.dumps({})


run(
    app,
    host=app.config.get('whrunner.host', '127.0.0.1'),
    port=int(app.config.get('whrunner.port', '8080')),
)
