from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO
from redis import Redis

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()

socketio = SocketIO(
    cors_allowed_origins="*",
)

redis_client: Redis | None = None
