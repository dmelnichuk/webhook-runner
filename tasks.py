import logging
import os
from typing import Callable

from invoke import task
from invoke.exceptions import Failure


logger = logging.Logger(name=__name__)
logger.parent = logger.root


def log(result: 'invoke.runners.Result'):
    """ Log invocation result. """
    if result.stdout:
        logger.info(result.stdout)
    if result.stderr:
        logger.error(result.stderr)


def hide_traceback(fn: Callable):
    """ Hide misleading traceback for `Failure` subclasses. """
    def wrapper(ctx, *args, **kwargs):
        try:
            fn(ctx, *args, **kwargs)
        except Failure as e:
            log(e.result)
            logger.error('Delivery was stopped.')

    return wrapper


def run_and_log(ctx: 'Context', cmd: str, warn: bool = True) -> bool:
    """
    Log and run command, then log and process its output.

    :param ctx: Invoke context,
    :param cmd: the command,
    :param warn: (optional) Invoke-compatible parameter. If you want to
     continue running commands after the current command being failed, set
     this parameter to True (default). If you want to stop the execution
     of all the next commands with the `Failure` exception, set it to False,
    :return: True if command was executed normally (has zero return code),
     False otherwise.
    """
    logger.info('Running command:\n{}'.format(cmd))

    result = ctx.run(cmd, hide='both', echo=False, warn=warn)
    log(result)
    if result.exited == 0:
        return True
    else:
        logger.error(
            'The last command exited with status {}'.format(result.exited)
        )
        return False


@task
@hide_traceback
def deploy(ctx):
    """ Deploy task. """
    name = ctx.config.get('github.name', 'master')
    base = os.path.expanduser(ctx.config.get('deploy.base', '~/www'))
    src = ctx.config.get('deploy.src', '.')
    scripts = ctx.config.get('deploy.scripts', '.')

    if not os.path.isdir(os.path.join(base, src)):
        # create source directory
        run_and_log(
            ctx,
            'mkdir -p {}'.format(os.path.join(base, src)),
            warn=False,
        )

    if not os.path.isdir(os.path.join(base, src, '.git')):
        # clone repository
        repo_url = ctx.config['github.url']
        with ctx.cd(base):
            run_and_log(
                ctx,
                'git clone "{}" {}'.format(repo_url, src),
                warn=False,
            )

    with ctx.cd(os.path.join(base, src)):
        run_and_log(ctx, 'git fetch', warn=False)
        run_and_log(ctx, 'git checkout {}'.format(name), warn=False)
        run_and_log(ctx, 'git pull', warn=False)

    if not os.path.isdir(os.path.join(base, 'env')):
        # TODO: automate it
        logger.error(
            'Please create virtual environment and set up services!'
        )

    else:
        with ctx.cd(base):
            # can't back up now, warn=True

            # issue Django commands
            run_and_log(
                ctx,
                'source env/bin/activate && pip install --upgrade pip'
            )
            run_and_log(
                ctx,
                'source env/bin/activate && pip install -r requirements.txt'
            )
            run_and_log(
                ctx,
                (
                    'source env/bin/activate'
                    ' && {}/manage.py migrate'
                ).format(scripts)
            )
            run_and_log(
                ctx, (
                    'source env/bin/activate'
                    ' && {}/manage.py collectstatic --noinput'
                ).format(scripts)
            )

            # restart services
            run_and_log(ctx, 'sudo systemctl restart gunicorn.service')
            run_and_log(ctx, 'sudo systemctl restart celery-worker.service')
            run_and_log(ctx, 'sudo systemctl restart celery-beat.service')

    logger.info('Delivery is completed normally.')


@task
@hide_traceback
def tag(ctx):
    """ Sync tags. """
    base = os.path.expanduser(ctx.config.get('deploy.base', '~/www'))
    src = ctx.config.get('deploy.src', '.')

    with ctx.cd(os.path.join(base, src)):
        run_and_log(ctx, 'git fetch --tags', warn=False)
