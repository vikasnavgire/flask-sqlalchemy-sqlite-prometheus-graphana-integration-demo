## Applications errors handling

class AppException(Exception):
    def __init__(self, message="Internal server error", reason=None, code=500):
        self.message = message
        self.reason = reason
        self.status_code = code

    def error_response(self):
        return {
            "status": "failed",
            "message": self.message,
            "reason": self.reason,
            "status_code": self.code
        }


class BadRequestException(AppException):
    def __init__(self, message="Bad request", reason=None, code=400):
        pass


class Unauthorized(AppException):
    def __init__(self, message="Unauthorised user", reason=None, code=403):
        pass
