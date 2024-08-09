import pytest

from fastapi_manager.apps import AppConfig
from fastapi_manager.core.exceptions import ImproperlyConfigured


class Stub:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


class TestAppConfig:
    """Unit tests for AppConfig class."""

    def test_path_set_explicitly(self):
        """If subclass sets path as class attr, no module attributes needed."""

        class MyAppConfig(AppConfig):
            path = "foo"

        ac = MyAppConfig("label", Stub())

        assert ac.path == "foo"

    def test_explicit_path_overrides(self):
        """If path set as class attr, overrides __path__ and __file__."""

        class MyAppConfig(AppConfig):
            path = "foo"

        ac = MyAppConfig("label", Stub(__path__=["a"], __file__="b/__init__.py"))

        assert ac.path == "foo"

    def test_dunder_path(self):
        """If single element in __path__, use it (in preference to __file__)."""
        ac = AppConfig("label", Stub(__path__=["a"], __file__="b/__init__.py"))

        assert ac.path == "a"

    def test_no_dunder_path_fallback_to_dunder_file(self):
        """If there is no __path__ attr, use __file__."""
        ac = AppConfig("label", Stub(__file__="b/__init__.py"))

        assert ac.path == "b"

    def test_empty_dunder_path_fallback_to_dunder_file(self):
        """If the __path__ attr is empty, use __file__ if set."""
        ac = AppConfig("label", Stub(__path__=[], __file__="b/__init__.py"))

        assert ac.path == "b"

    def test_multiple_dunder_path_fallback_to_dunder_file(self):
        """If the __path__ attr is length>1, use __file__ if set."""
        ac = AppConfig("label", Stub(__path__=["a", "b"], __file__="c/__init__.py"))

        assert ac.path == "c"

    def test_no_dunder_path_or_dunder_file(self):
        """If there is no __path__ or __file__, raise ImproperlyConfigured."""
        with pytest.raises(ImproperlyConfigured):
            AppConfig("label", Stub())

    def test_empty_dunder_path_no_dunder_file(self):
        """If the __path__ attr is empty and there is no __file__, raise."""
        with pytest.raises(ImproperlyConfigured):
            AppConfig("label", Stub(__path__=[]))

    def test_multiple_dunder_path_no_dunder_file(self):
        """If the __path__ attr is length>1 and there is no __file__, raise."""
        with pytest.raises(ImproperlyConfigured):
            AppConfig("label", Stub(__path__=["a", "b"]))

    def test_duplicate_dunder_path_no_dunder_file(self):
        """
        If the __path__ attr contains duplicate paths and there is no
        __file__, they duplicates should be deduplicated (#25246).
        """
        ac = AppConfig("label", Stub(__path__=["a", "a"]))
        assert ac.path == "a"

    def test_repr(self):
        ac = AppConfig("label", Stub(__path__=["a"]))
        assert repr(ac) == "<AppConfig: label>"

    def test_invalid_label(self):
        class MyAppConfig(AppConfig):
            label = "invalid.label"

        msg = "The app label 'invalid.label' is not a valid Python identifier."
        with pytest.raises(ImproperlyConfigured, match=msg):
            MyAppConfig("test_app", Stub())
