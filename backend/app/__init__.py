from flask import Flask
from redis import Redis

from app.config import Config
from app.extensions import db, migrate, jwt, socketio
import app.extensions as extensions


def create_app() -> Flask:
    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    from app.users import models

    migrate.init_app(app, db)
    jwt.init_app(app)

    socketio.init_app(
        app,
        cors_allowed_origins=["http://localhost:5173"],
    )

    extensions.redis_client = Redis.from_url(
        app.config["REDIS_URL"],
        decode_responses=True,
    )

    register_blueprints(app)

    return app


def register_blueprints(app: Flask) -> None:
    from app.users.routes import users_bp

    app.register_blueprint(
        users_bp,
        url_prefix="/api/v1/users",
    )
