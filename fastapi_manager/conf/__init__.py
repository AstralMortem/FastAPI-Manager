import os

from dynaconf import LazySettings
from pathlib import Path

GLOBAL_SETTINGS_PATH = Path(__file__).parent.joinpath("global_settings.py").absolute()
SETTINGS_ENVIRON = "FASTAPI_SETTINGS"
print(os.environ.get(SETTINGS_ENVIRON))

settings = LazySettings(
    environments=True,
    load_dotenv=True,
    settings_files=[
        str(GLOBAL_SETTINGS_PATH),
        str(os.environ.get(SETTINGS_ENVIRON, None)),
    ],
    merge_enabled=True,
    envvar_prefix="FASTAPI",
)
