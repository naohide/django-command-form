from __future__ import annotations

import io
import json
from contextlib import redirect_stdout
from importlib.util import find_spec
from pathlib import Path
from textwrap import dedent
from typing import Any

from django.apps import apps
from django.core import management

from .models import CommandModel


def get_command_models(app_name: str) -> list[CommandModel]:
    commands: list[CommandModel] = []

    for app_config in apps.get_app_configs():
        if app_name not in app_config.name.split("."):
            continue

        spec = find_spec(f"{app_config.name}.management")
        if spec and spec.loader and hasattr(spec.loader, "path"):
            commands.extend(
                CommandModel(
                    app_name=app_config.verbose_name.title(),
                    command_name=command_name,
                )
                for command_name in management.find_commands(
                    str(Path(spec.loader.path).parent)
                )
            )
    return commands


def get_command_contents(
    app_name: str,
    command_name: str,
) -> tuple[str, str]:
    spec = find_spec(f"{app_name}.management.commands.{command_name}")
    if spec and spec.loader and hasattr(spec.loader, "path"):
        return spec.loader.get_data(spec.loader.path).decode()  # type: ignore[no-any-return, attr-defined]
    msg = f"Command {command_name} not found in {app_name}"
    raise ValueError(msg)


def run_command(
    command_name: str,
    cleaned_data: dict[str, Any],
) -> str:
    args = [item for pair in cleaned_data.items() for item in pair]
    try:
        capture = io.StringIO()
        with redirect_stdout(capture):
            management.call_command(command_name, *args)
        return capture.getvalue() or "Completed to execute"
    except Exception as e:  # noqa: BLE001
        return dedent(
            f"""
            Unable to run management command {command_name}
            with {json.dumps(args)} - {e!s}
            """,
        )
