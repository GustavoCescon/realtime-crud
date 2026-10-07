from flask import Flask, jsonify
from pydantic import ValidationError

from app.common.exceptions import AppError

def register_error_handlers(app: Flask) -> None:
    @app.errorhandler(AppError)
    def handle_app_error(error: AppError):
        return jsonify({
            "error": error.error_code,
            "message": error.message,
        }), error.status_code

    @app.errorhandler(ValidationError)
    def handle_validation_error(error: ValidationError):
        return jsonify({
            "error": "validation_error",
            "details": error.errors(include_url=False),
        }), 422
