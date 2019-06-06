# Webhook Runner

Simple CD tool for Django, that listens to GitHub webhook `push` event, then
updates project, models, static files, and restarts services.

Written in Python 3.

Read more about GitHub webhooks [here](https://developer.github.com/webhooks/).

## Setup

### 1. Prepare Python environment

I recommend using [virtualenv](https://virtualenv.pypa.io/). Create an
environment with the required version of Python, then activate it:

```bash
$ virualenv -p python3 env
$ source env/bin/activate
(env)$
```

If you are prefer using system or user environment, skip this step.

### 2. Install dependencies

All dependencies are listed in `requirements.txt`. It is a `pip` response
file.

```bash
(env)$ pip install -r requirements.txt
```

### 3. Write `config.ini`

Here is a run-down of its sections:

#### `[whrunner]`
- `host` − host address to bind. Default: '127.0.0.1',
- `port` − port to listen to. Default: 8080.

#### `[logging]`
- `level` − level of logging messages. Most useful values are 'ERROR' and
'INFO'.

#### `[github]`
- `name` − a name of the branch or tag to deliver. Default: 'master',
- `secret` − webhook secret. Just a free-form string of characters,
preferably random. See
[GitHub documentation](https://developer.github.com/webhooks/creating/#setting-up-a-webhook)
for further details,
- `url` − URL ot the git repository.

#### `[deploy]`
- `base` − base path to the Django project folder, commonly referred to as
`BASE_DIR`. May contain other directories (source, media, static, et c.).
Home expansion (~) is allowed,
- `src` − a relative path to the project's git source (the directory with
`.git` directory inside). May be the same as base ('.'),
- `scripts` − a directory where `manage.py` and other project-level scripts
are stored. May be the same as base ('.').

A `config.ini.example` file is included for your convenience.

### 4. Launch `runner.py` as a service

You can use application servers like [gunicorn](https://gunicorn.org/) or
[uwsgi](https://uwsgi-docs.readthedocs.io/). Refer to the relevant
documentation. The module name is `runner.app`.

Alternatively, you can use an app server that is already shipped with
[bottle](https://bottlepy.org/), the main dependency:

```bash
(env)$ python3 runner.py
```

### 5. Set up a webhook on GitHub

- “Payload URL” must end with `/webhook/` (note the trailing slash):

  http://cd.example.com/webhook/

- “Content type” must be “application/json”.

Please read the [GitHub
documentation](https://developer.github.com/webhooks/creating/#setting-up-a-webhook)
about webhook settings in general.