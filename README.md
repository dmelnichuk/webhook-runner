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

Refer to the `config.ini.example` file.

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

[Setting up a
webhook](https://developer.github.com/webhooks/creating/#setting-up-a-webhook).
