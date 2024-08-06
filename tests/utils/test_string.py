from fastapi_manager.utils.string import convert_to_snake_case, convert_to_camel_case


def test_convert_to_snake_case():
    assert convert_to_snake_case("test") == "test"
    assert convert_to_snake_case("Test") == "test"
    assert convert_to_snake_case("TestTest") == "test_test"
    assert convert_to_snake_case("TestTestTest") == "test_test_test"
    assert convert_to_snake_case("TESTTest") == "test_test"


def test_convert_to_camel_case():
    assert convert_to_camel_case("test") == "test"
    assert convert_to_camel_case("Test") == "test"
    assert convert_to_camel_case("TestTest") == "testtest"
    assert convert_to_camel_case("Test_Test_Test") == "testTestTest"
