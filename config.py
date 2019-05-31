import os

import bottle


CONFIG_FILE = os.path.join(os.path.dirname(__name__), 'config.ini')

app = bottle.default_app()
app.config.load_config(CONFIG_FILE)
