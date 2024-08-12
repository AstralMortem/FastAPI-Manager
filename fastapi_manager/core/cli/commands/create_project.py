import os
import shutil
from pathlib import Path

from fastapi_manager.core.cli.base import BaseCommand
from fastapi_manager.utils.filesystem import (
    PathChecker,
    PROJECT_TEMPLATE_DIR,
    TEMPLATE_SUFFIX,
    TemplateDoesNotExists,
    replace_vars_in_file,
)


class StartNewProject(BaseCommand):
    command_name = "startproject"

    def __init__(self, project_name, project_path: Path = None, settings: str = None):
        super().__init__(settings)
        self.project_name = project_name
        self.project_path = project_path
        self.placeholders = {"{{project_name}}": self.project_name}

        self.execute()

    def get_destination(self):
        if self.project_path is not None:
            if self.project_path == ".":
                return PathChecker(self.project_path).is_empty().as_path()
            return PathChecker(self.project_path).is_exists().is_empty().as_path()
        path = (
            PathChecker(Path(".").joinpath(self.project_name)).is_not_exists().as_path()
        )
        path.mkdir()
        return path

    def copy_folder(self):
        destination = self.get_destination()
        if not PROJECT_TEMPLATE_DIR.exists():
            raise TemplateDoesNotExists("Project template does not exist")
        for root, dirs, files in PROJECT_TEMPLATE_DIR.walk():
            relative = root.relative_to(PROJECT_TEMPLATE_DIR)
            dest_dir = destination.joinpath(relative)
            if dest_dir.name.startswith("{{"):
                dest_dir = dest_dir.with_name(self.project_name)

            if not dest_dir.exists():
                dest_dir.mkdir()

            for filename in files:
                if filename.endswith(TEMPLATE_SUFFIX):
                    src_file = root.joinpath(filename)
                    dest_filename = filename.rsplit(TEMPLATE_SUFFIX, 1)[0]
                    dest_file = dest_dir.joinpath(dest_filename)
                    shutil.copy(src_file, dest_file)
                    replace_vars_in_file(self.placeholders, dest_file)

        return destination

    def _action(self):
        self.copy_folder()
