from pathlib import Path
import os
import shutil
import fastapi_manager
from fastapi_manager.conf import settings

TEMPLATE_PATH = (
    Path(fastapi_manager.__file__)
    .parent.joinpath("conf")
    .joinpath("templates")
    .absolute()
)


class TemplateHandler:
    template_path = TEMPLATE_PATH
    template_prefix: str
    template_sufix = "-tpl"
    new_template_name: str = ""
    destination_path: str = None
    replacement: dict[str, str]

    def __init__(self, name):
        self.new_template_name = name

    def _action(self):
        raise NotImplemented

    def _get_full_template_path(self):
        return self.template_path.joinpath(self.template_prefix).absolute()

    def _replace_text_in_files(
        self,
        source,
    ):
        with open(source, "r", encoding="utf-8") as file:
            content = file.read()
            for placeholder, value in self.replacement.items():
                if placeholder in content:
                    content = content.replace(placeholder, value)
            with open(source, "w", encoding="utf-8") as file:
                file.write(content)

    def _get_destination(self):
        if self.destination_path and self.destination_path != ".":
            new_path = Path(self.destination_path)

        if self.destination_path == ".":
            new_path = Path(".").joinpath("/")
            if len(new_path.iterdir()) > 0:
                raise Exception("Folder is not empty")
            if not new_path.exists():
                raise Exception("Folder does not exist")

        if self.destination_path is None:
            new_path = Path(".").joinpath(self.new_template_name)
            if new_path.exists():
                raise Exception("Folder already exist")

        return new_path.absolute()

    def execute(self):
        return self._action()


class CreateProject(TemplateHandler):
    def __init__(self, name, path, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.template_prefix = "[project_name]"
        self.destination_path = path
        self.replacement = {"{{ project_name }}": self.new_template_name}

    def _action(self):
        dest_folder = self._get_destination()
        src_folder = self._get_full_template_path()

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        for root, dirs, files in os.walk(src_folder):
            # Determine the relative path from the source root
            relative_path = os.path.relpath(root, src_folder)
            if relative_path.startswith("["):
                relative_path = self.new_template_name
            # Create corresponding directory in the destination folder
            dest_dir = os.path.join(dest_folder, relative_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # Process files in the current directory
            for filename in files:
                if filename.endswith(self.template_sufix):
                    # Define the source and destination file paths
                    src_file = os.path.join(root, filename)
                    # Remove the -tpl suffix from the filename
                    dest_filename = filename.rsplit(self.template_sufix, 1)[0]
                    dest_file = os.path.join(dest_dir, dest_filename)

                    # Copy the file to the destination folder
                    new_destination = shutil.copy(src_file, dest_file)
                    self._replace_text_in_files(new_destination)


class StartApp(TemplateHandler):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        self.template_prefix = "[app_name]"
        self.destination_path = settings.BASE_DIR
        self.replacement = {
            "{{ app_name }}": self.new_template_name,
            "{{ camel_case_app_name }}": self._format_to_camel_case(),
        }

    def _format_to_camel_case(self):
        return "".join(map(lambda x: x.capitalize(), self.new_template_name.split("_")))

    def _action(self):
        dest_folder = self._get_destination()
        src_folder = self._get_full_template_path()

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        for root, dirs, files in os.walk(src_folder):
            # Determine the relative path from the source root
            relative_path = os.path.relpath(root, src_folder)
            if relative_path.startswith("["):
                relative_path = self.new_template_name
            # Create corresponding directory in the destination folder
            dest_dir = os.path.join(dest_folder, relative_path)
            if not os.path.exists(dest_dir):
                os.makedirs(dest_dir)

            # Process files in the current directory
            for filename in files:
                if filename.endswith(self.template_sufix):
                    # Define the source and destination file paths
                    src_file = os.path.join(root, filename)
                    # Remove the -tpl suffix from the filename
                    dest_filename = filename.rsplit(self.template_sufix, 1)[0]
                    dest_file = os.path.join(dest_dir, dest_filename)

                    # Copy the file to the destination folder
                    shutil.copy(src_file, dest_file)
                    self._replace_text_in_files(new_destination)
