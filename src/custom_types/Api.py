from typing import Any, List


class ApiResponse():
    def __init__(self, error: bool, message: List[str]):
        self.error = error
        self.message = message


class ApiResponsePayload(ApiResponse):
    def __init__(self, error: bool, message: List[str], payload: Any):
        super().__init__(error, message)
        self.payload = payload
