from pathlib import Path

import pytest

from fastapi_manager.utils.filesystem import (
    PathChecker,
    PathDoesNotExist,
    PathAlreadyExists,
    PathIsNotEmpty,
)


def test_path_checker_class():
    checker = PathChecker(".")
    assert checker.as_path() == Path(".").absolute()


def test_exists_path_flags():
    checker = PathChecker(".")
    assert checker.is_exists().as_path() == Path(".").absolute()
    with pytest.raises(PathAlreadyExists):
        checker.is_not_exists().as_path()


def test_empty_path_flags():
    checker = PathChecker(".")
    assert checker.is_not_empty().as_path() == Path(".").absolute()
    with pytest.raises(PathIsNotEmpty):
        checker.is_empty().as_path()


def test_dir_path_flags():
    checker = PathChecker(".")
    assert checker.is_dir().as_path() == Path(".").absolute()
    with pytest.raises(Exception):
        checker.is_not_dir().as_path()


def test_file_path_flags():
    checker = PathChecker(".")
    assert checker.is_not_file().as_path() == Path(".").absolute()
    with pytest.raises(Exception):
        checker.is_file().as_path()
