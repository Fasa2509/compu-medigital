from typing import Any


class ApiResponse():
    def __init__(self, error: bool, message: list[str]):
        self.error = error
        self.message = message


class ApiResponsePayload(ApiResponse):
    def __init__(self, error: bool, message: list[str], payload: Any):
        super().__init__(error, message)
        self.payload = payload
