import pytest

from fastapi_manager.utils.lazy import LazyObject, LazyFactory, empty


class ObjectTest:
    field_1: str = "field_1"
    field_2: int = 1

    def __init__(self):
        self.field_3: int = 2

    def method_1(self):
        return "method_1"

    def method_2(self):
        return "method_2"

    @property
    def property(self):
        return "property"


@pytest.fixture
def lazy_obj():
    return LazyFactory(lambda: ObjectTest())


def test_initial_value(lazy_obj):
    assert lazy_obj._wrapped is empty


def test_value_computation(lazy_obj):
    instance = lazy_obj.field_1
    assert instance == "field_1"
    assert lazy_obj.field_1 == "field_1"


def test_all_values(lazy_obj):
    for key, value in lazy_obj.__dict__.items():
        if key in ["_setupfunc", "_wrapped"]:
            continue
        assert lazy_obj.__dict__[key] == ObjectTest.__dict__[key]


def test_changes(lazy_obj):
    lazy_obj.field_1 = "new_field_1"
    assert lazy_obj.field_1 == "new_field_1"
    assert lazy_obj._wrapped.field_1 == "new_field_1"


def test_delete(lazy_obj):
    assert lazy_obj.field_1 == "field_1"
    with pytest.raises(AttributeError):
        del lazy_obj.field_1

    assert lazy_obj.field_3 == 2
    del lazy_obj.field_3
    with pytest.raises(AttributeError):
        assert lazy_obj.field_3
