import os

import dynaconf
from dynaconf import Dynaconf
from pathlib import Path

GLOBAL_SETTINGS_PATH = Path(__file__).parent.joinpath("global_settings.py").absolute()
SETTINGS_ENVIRON = "FASTAPI_SETTINGS"

dynaconf.utils.parse_conf.converters["@path"] = lambda x: Path(x).absolute()

settings = Dynaconf(
    environments=True,
    load_dotenv=True,
    settings_files=[
        str(GLOBAL_SETTINGS_PATH),
        str(os.environ.get(SETTINGS_ENVIRON, None)),
    ],
    merge_enabled=True,
    envvar_prefix="FASTAPI",
)
