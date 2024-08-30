import pytest

from contextlib import nullcontext as does_not_raise


def test_insert_values(settings):
    settings.DEBUG = True
    settings.INSTALLED_APPS = []
    settings.MIDLEWARE = []


@pytest.mark.parametrize(
    "key, value, expected",
    [
        ("DEBUG", True, does_not_raise()),
        ("INSTALLED_APPS", [], does_not_raise()),
        ("MIDLEWARE", [], does_not_raise()),
        ("NOT_EXISTS", True, pytest.raises(AttributeError)),
    ],
)
def test_settings_functions(key, value, expected, settings):
    with expected:
        assert getattr(settings, key) == value


def test_settings_exception(settings):
    with pytest.raises(AttributeError):
        assert settings.smth


def test_settings_path_converor(settings):
    from pathlib import Path

    assert isinstance(settings.BASE_DIR, Path)
