import os
from pathlib import Path
import shutil
import fastapi_manager

TEMPLATE_PATH = Path(fastapi_manager.__file__).parent.joinpath("templates")


class TemplateHandler:
    template_placeholder: str
    template_sufix: str = "-tpl"
    placeholders: dict[str, str]

    def __init__(self, name: str, path: Path | None = None):
        self.name = name
        self.path = path
        self.template_path = self._check_src_path(
            TEMPLATE_PATH.joinpath(self.template_placeholder).absolute()
        )
        self.destination_path = self._get_destination_path(path)

        self.create = False

        self.placeholders = {self.template_placeholder: self.name}

    def _get_destination_path(self, path: Path | None):
        destination_path: Path
        if path:
            destination_path = self._check_dest_path(path.absolute())
        else:
            destination_path = self._check_dest_path(
                Path(".").absolute().joinpath(self.name)
            )
        return destination_path

    def _check_src_path(self, src: Path):
        if not os.path.exists(src):
            raise Exception("Template folder does not exists")
        return src

    def _check_dest_path(self, dest: Path):
        if dest.exists():
            list_dir = os.listdir(dest)
            if len(list_dir) > 0:
                raise Exception("Destination folder already exist and not empty")
            if self.name in list_dir:
                raise Exception("Folder with same name already exists")
        self.create = True
        return dest

    def _replace_placeholders_in_file(self, file_path):
        if self.placeholders:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                for placeholder, value in self.placeholders.items():
                    if placeholder in content:
                        content = content.replace(placeholder, value)
                with open(file_path, "w", encoding="utf-8") as file:
                    file.write(content)

    def copy_template(self):
        try:
            if self.create:
                os.makedirs(self.destination_path)

            for root, dirs, files in os.walk(self.template_path):
                relative_path = os.path.relpath(root, self.template_path)
                if relative_path.startswith("{{"):
                    relative_path = self.name

                dest_dir = os.path.join(self.destination_path, relative_path)
                if not os.path.exists(dest_dir):
                    os.makedirs(dest_dir)

                for folder in dirs:
                    if folder.startswith("{{"):
                        continue
                    sub_folder = os.path.join(dest_dir, folder)
                    if not os.path.exists(sub_folder):
                        os.makedirs(sub_folder)

                for filename in files:
                    if filename.endswith(self.template_sufix):
                        src_file = os.path.join(root, filename)
                        dest_filename = filename.rsplit(self.template_sufix, 1)[0]
                        dest_file = os.path.join(dest_dir, dest_filename)

                        # Copy the file to the destination folder
                        shutil.copy(src_file, dest_file)
                        # replace placeholders in files
                        self._replace_placeholders_in_file(dest_file)
        except Exception as error:
            print(error)


class NewProjectHandler(TemplateHandler):
    template_placeholder: str = "{{project_name}}"


class NewAppHandler(TemplateHandler):
    template_placeholder: str = "{{app_name}}"

    def _check_dest_path(self, dest: Path):
        return dest.joinpath(self.name)
