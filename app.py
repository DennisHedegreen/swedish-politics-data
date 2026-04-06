import os

os.environ.setdefault("WPD_APP_TITLE", "Swedish Politics Data")
os.environ.setdefault("WPD_EXPOSE_COUNTRIES", "sweden")

from engine_app import main


main()
