#!/usr/bin/env python
import os
import sys


def main():
    os.environ.setdefault("SETTINGS_MODULE", "projects.settings")
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
