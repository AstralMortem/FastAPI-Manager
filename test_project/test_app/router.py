from fastapi_manager.router import BaseRouter

ENDPOINTS = BaseRouter(prefix="/test-app")


@ENDPOINTS.get("")
def index():
    return {"message": "Hello World"}
