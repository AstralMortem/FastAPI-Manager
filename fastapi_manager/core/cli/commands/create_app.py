import shutil
from pathlib import Path

from fastapi_manager.core.cli.base import BaseCommand
from fastapi_manager.conf import settings as conf
from fastapi_manager.utils.filesystem import (
    PathChecker,
    APP_TEMPLATE_DIR,
    TEMPLATE_SUFFIX,
    TemplateDoesNotExists,
    replace_vars_in_file,
)
from fastapi_manager.utils.string import convert_to_camel_case


class StartNewApp(BaseCommand):
    command_name = "startapp"

    def __init__(self, app_name: Path, settings: str = None):
        super().__init__(settings)
        self.app_name = app_name
        self.app_path = conf.BASE_DIR.joinpath(app_name)
        print(self.app_path)
        self.placeholders = {
            "{{app_name}}": app_name,
            "{{project_name}}": str(conf.BASE_DIR.name),
            "{{camel_case_app_name}}": convert_to_camel_case(str(app_name)),
        }
        self.execute()

    def get_destination(self):
        app_path = PathChecker(self.app_path).is_not_exists().as_path()
        app_path.mkdir()
        return app_path

    def copy_folder(self):
        destination = self.get_destination()
        if not APP_TEMPLATE_DIR.exists():
            raise TemplateDoesNotExists("App template does not exist")
        for root, dirs, files in APP_TEMPLATE_DIR.walk():
            relative = root.relative_to(APP_TEMPLATE_DIR)
            dest_dir = destination.joinpath(relative)
            if dest_dir.name.startswith("{{"):
                dest_dir = dest_dir.with_name(self.app_name)

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
