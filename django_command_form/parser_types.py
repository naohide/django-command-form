from __future__ import annotations

import datetime
import json
from argparse import ArgumentTypeError


def date(value: str) -> datetime.date:
    try:
        return datetime.date.fromisoformat(value)
    except ValueError as e:
        msg = f'"{value}" is not a valid date format'
        raise ArgumentTypeError(msg) from e


def date_time(value: str) -> datetime.datetime:
    try:
        return datetime.datetime.fromisoformat(value)
    except ValueError as e:
        msg = f'"{value}" is not a valid datetime format'
        raise ArgumentTypeError(msg) from e


def json_string(value: str) -> str:
    try:
        json.loads(value)
    except json.JSONDecodeError as e:
        msg = f"{value} is not a valid JSON string"
        raise ArgumentTypeError(msg) from e
    return value
