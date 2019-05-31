import os

from invoke import task


@task
def deploy(ctx, name, base, src):

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
