import os
import shutil
from pathlib import Path

from core.cli.base import BaseCommand
import fastapi_manager.templates as templates


class ProjectAlreadyExists(Exception):
    pass


class DirectoryDoesNotExists(Exception):
    pass


class DirectoryIsNotEmpty(Exception):
    pass


class TemplateDoesNotExists(Exception):
    pass


# get template path
TEMPLATE_PATH = Path(templates.__file__).parent
TEMPLATE_SUFFIX = "-tpl"


def replace_placeholders_in_file(placeholders, file_path):
    if placeholders:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            for placeholder, value in placeholders.items():
                if placeholder in content:
                    content = content.replace(placeholder, value)
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)


class StartNewProject(BaseCommand):
    def __init__(self, project_name, project_path: Path | str | None = None):
        self.project_name = project_name
        self.project_path = project_path

        self.full_template_path = TEMPLATE_PATH.joinpath("{{project_name}}").absolute()
        self.destination_path = self.get_destination(create_dirs=True)
        self.placeholders = {"{{project_name}}": self.project_name}

    def get_destination(self, create_dirs=True):
        path: Path
        if self.project_path is None:
            path = Path(".").absolute().joinpath(self.project_name)
            if path.exists():
                raise ProjectAlreadyExists("Project with same name already exists")
            if create_dirs:
                path.mkdir()
            return path
        if self.project_path == ".":
            path = Path(".").parent.absolute().joinpath()
            if len(list(path.iterdir())) > 0:
                raise DirectoryIsNotEmpty("Destination folder is not empty")
            return path
        path = Path(self.project_path).absolute()
        if not path.exists():
            raise DirectoryDoesNotExists("Destination folder does not exist")
        if len(list(path.iterdir())) > 0:
            raise DirectoryIsNotEmpty("Destination folder is not empty")
        return path

    def copy_folder(self):
        if not self.full_template_path.exists():
            raise TemplateDoesNotExists("Project template does not exist")
        for root, dirs, files in self.full_template_path.walk():
            relative = root.relative_to(self.full_template_path)
            dest_dir = self.destination_path.joinpath(relative)
            if dest_dir.name.startswith("{{"):
                dest_dir = dest_dir.with_name(self.project_name)

            if not dest_dir.exists():
                dest_dir.mkdir()

            for filename in files:
                if filename.endswith(TEMPLATE_SUFFIX):
                    src_file = os.path.join(root, filename)
                    dest_filename = filename.rsplit(TEMPLATE_SUFFIX, 1)[0]
                    dest_file = os.path.join(dest_dir, dest_filename)
                    shutil.copy(src_file, dest_file)
                    replace_placeholders_in_file(self.placeholders, dest_file)
