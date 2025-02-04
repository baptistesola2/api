from flask import Flask
from loguru import logger

from .api import blueprint as api_blueprint
from .tools import tools_bp
from .config import config
from .log import InterceptHandler
from .redis import redis_client


def create_app(env):
    app = Flask(__name__, instance_relative_config=True)

    # Load default config
    app.config.from_object(config[env])

    # Log to loguru
    logger.add(
        app.config["LOGFILE"],
        level=app.config["LOG_LEVEL"],
        format="{time} {level} {message}",
        backtrace=app.config["LOG_BACKTRACE"],
    )
    app.logger.addHandler(InterceptHandler())

    # Init RabbitMQ
    from .amqp import ramq

    ramq.init_app(app=app)

    # Init Redis
    redis_client.init_app(app=app)

    # API Blueprint
    app.register_blueprint(api_blueprint)

    # Technical routes
    app.register_blueprint(tools_bp, url_prefix="/tools")

    app.logger.info("Running on %s", app.config["REDIS_URL"])

    return app
