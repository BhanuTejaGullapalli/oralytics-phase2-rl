# src/server/__init__.py

import os

from flask import Flask
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
import logging

logging.basicConfig(
    filename="./data/logs/API_log.txt",
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(name)s %(threadName)s : %(message)s",
)
app = Flask(__name__)
CORS(app)

app_settings = os.getenv("APP_SETTINGS", "src.server.config.DevelopmentConfig")
app.config.from_object(app_settings)

bcrypt = Bcrypt(app)
db = SQLAlchemy(app,
                engine_options={"query_cache_size": 0},)

migrate = Migrate()
migrate.init_app(app, db)

from src.server.auth.views import auth_blueprint

app.register_blueprint(auth_blueprint)

from src.server.main import rlservice_blueprint

app.register_blueprint(rlservice_blueprint)

app.logger.info("Server started")

# Check if the server is being restarted
if app.config.get("RESTART"):
    print("Server is being restarted")
    app.logger.info("Server is being restarted")
    from src.server.restart import restart_server
    restart_server(app)
    # app.config["RESTART"] = False