import os

os.environ.setdefault("WPD_APP_TITLE", "Swedish Political Data")
os.environ.setdefault("WPD_EXPOSE_COUNTRIES", "sweden")

from engine_app import *  # noqa: F401,F403
