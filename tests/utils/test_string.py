import pytest

from fastapi_manager.utils.string import (
    convert_to_snake_case,
    convert_to_camel_case,
    is_camel_case,
    is_snake_case,
)


@pytest.mark.parametrize(
    "string, result",
    [
        ("test", "test"),
        ("Test", "test"),
        ("TestTest", "test_test"),
        ("TestTestTest", "test_test_test"),
        ("Test_test_Test", "test_test_test"),
        ("testTestTesttest", "test_test_testtest"),
    ],
)
def test_convert_to_snake_case(string, result):
    assert convert_to_snake_case(string) == result


@pytest.mark.parametrize(
    "string, result",
    [
        ("test", "test"),
        ("Test", "test"),
        ("TestTest", "testtest"),
        ("Test_Test_Test", "testTestTest"),
        ("test_Test_test", "testTestTest"),
    ],
)
def test_convert_to_camel_case(string, result):
    assert convert_to_camel_case(string) == result


@pytest.mark.parametrize(
    "string, result",
    [
        ("test", "Test"),
        ("Test", "Test"),
        ("TestTest", "Testtest"),
        ("Test_Test_Test", "TestTestTest"),
        ("test_Test_test", "TestTestTest"),
    ],
)
def test_convert_to_pascal_case(string, result):
    assert convert_to_camel_case(string, True) == result


@pytest.mark.parametrize(
    "string, result",
    [
        ("TestTest", True),
        ("testTest", True),
        ("Test_test", False),
        ("testTest_testTest_Test", False),
    ],
)
def test_camel_cases(string, result):
    assert is_camel_case(string) == result


@pytest.mark.parametrize(
    "string, result",
    [
        ("TestTest", False),
        ("testTest", False),
        ("Test_test", False),
        ("testTest_testTest_Test", False),
        ("test_test", True),
        ("test_test_test_test", True),
    ],
)
def test_snake_cases(string, result):
    assert is_snake_case(string) == result
