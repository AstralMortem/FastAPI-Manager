from pathlib import Path
from fastapi_manager import templates

TEMPLATE_SUFFIX = "-tpl"
TEMPLATE_DIR = Path(templates.__file__).parent.absolute()
PROJECT_TEMPLATE_DIR = TEMPLATE_DIR.joinpath("{{project_name}}").absolute()
APP_TEMPLATE_DIR = TEMPLATE_DIR.joinpath("{{app_name}}").absolute()


class PathIsNotEmpty(Exception):
    pass


class PathIsEmpty(Exception):
    pass


class PathDoesNotExist(Exception):
    pass


class PathAlreadyExists(Exception):
    pass


class TemplateDoesNotExists(Exception):
    pass


class PathChecker:
    def __init__(self, path: Path | str):
        self.path = Path(path).absolute()

    def _is_empty(self):
        return len(list(self.path.iterdir())) == 0

    def is_empty(self):
        if self._is_empty():
            return self
        raise PathIsNotEmpty(f"{self.path} is not empty")

    def is_not_empty(self):
        if not self._is_empty():
            return self
        raise PathIsEmpty(f"{self.path} is empty")

    def is_exists(self):
        if self.path.exists():
            return self
        raise PathDoesNotExist(f"{self.path} does not exist")

    def is_not_exists(self):
        if not self.path.exists():
            return self
        raise PathAlreadyExists(f"{self.path} already exists")

    def is_dir(self):
        if self.path.is_dir():
            return self
        raise PathDoesNotExist(f"{self.path} does not exist")

    def is_not_dir(self):
        if not self.path.is_dir():
            return self
        raise PathAlreadyExists(f"{self.path} already exists")

    def is_file(self):
        if self.path.is_file():
            return self
        raise PathDoesNotExist(f"{self.path} does not exist")

    def is_not_file(self):
        if not self.path.is_file():
            return self
        raise PathAlreadyExists(f"{self.path} already exists")

    def as_path(self):
        return self.path.absolute()

    def __repr__(self):
        return str(self.path)

    def __str__(self):
        return str(self.path)


# overrides {{}} vars in files, by placeholders
def replace_vars_in_file(vars: dict, file_path: Path | str):
    if vars:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            for placeholder, value in vars.items():
                if placeholder in content:
                    content = content.replace(placeholder, str(value))
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
