class AppError(Exception):
    status_code = 500
    error_code = "internal_server_error"

    def __init__(self, message: str | None = None):
        super().__init__(message)
        self.message = message

class UserNotFoundError(AppError):
    status_code = 404
    error_code = "user_not_found"

class UserAlreadyExistsError(AppError):
    status_code = 409
    error_code = "email_already_exists"

class InvalidCredentialsError(AppError):
    status_code = 401
    error_code = "invalid_credentials"
