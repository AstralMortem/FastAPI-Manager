from fastapi_manager.router import path, include

ENDPOINTS = [path("/", include("test_app.router"))]
