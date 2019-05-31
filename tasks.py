import os

from invoke import task


@task
def deploy(ctx):
    name = ctx.config.get('github.name', 'master')
    base = os.path.expanduser(ctx.config.get('deploy.base', '~/www'))
    src = ctx.config.get('deploy.src', '.')

    # no source directory found − create it
    if not os.path.isdir(os.path.join(base, src)):
        ctx.run('mkdir -p {}'.format(os.path.join(base, src)))

    # no repository found − clone it
    if not os.path.isdir(os.path.join(base, src, '.git')):
        repo_url = ctx.config['github.url']
        with ctx.cd(base):
            ctx.run('git clone "{}" {}'.format(repo_url, src))

    with ctx.cd(os.path.join(base, src)):
        ctx.run('git fetch')
        ctx.run('git checkout {}'.format(name))

    with ctx.cd(base):
        ctx.run((
            'source env/bin/activate &&'
            ' pip install --upgrade pip &&'
            ' pip install -r requirements.txt &&'
            ' ObeDog/manage.py migrate &&'
            ' ObeDog/manage.py collectstatic --noinput'
        ))

        ctx.run('sudo systemctl restart gunicorn.service')
        ctx.run('sudo systemctl restart celery-worker.service')
        ctx.run('sudo systemctl restart celery-beat.service')
