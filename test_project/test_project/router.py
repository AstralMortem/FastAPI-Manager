from fastapi_manager.router import path, include


endpoints = [
    path("/", include("test_app.router")),
]
