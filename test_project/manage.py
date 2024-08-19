#!/usr/bin/env python
from pathlib import Path
import os

PROJECT_DIR = Path(__file__).resolve().parent.absolute()


def main():
    os.environ.setdefault("FASTAPI_SETTINGS", "./test_project/settings.toml")
    os.environ.setdefault("PROJECT_DIR", str(PROJECT_DIR))
    try:
        from fastapi_manager.core.cli import cli
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Fastapi Manager. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    cli()


if __name__ == "__main__":
    main()
