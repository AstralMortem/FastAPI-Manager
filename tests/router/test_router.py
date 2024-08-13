from fastapi import APIRouter

from fastapi_manager.router import path, include, url_resolver


def test_include(settings):
    settings.INSTALLED_APPS = ["tests.apps.models_app"]
    router = include("tests.apps.models_app.router")
    assert router is APIRouter
