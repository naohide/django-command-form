from __future__ import annotations

import argparse
from typing import Any

from django import forms
from django.core import management

from .parser_types import date, date_time, json_string

_Fields = (
    forms.CharField
    | forms.IntegerField
    | forms.BooleanField
    | forms.ChoiceField
    | forms.FileField
)

_IGNORED_ARGUMENT_NAMES = [
    "configuration",
    "force_color",
    "help",
    "no_color",
    "pythonpath",
    "settings",
    "skip_checks",
    "traceback",
    "tty",
    "verbosity",
    "version",
]


class CommandForm(forms.Form):
    def __init__(
        self,
        command: management.BaseCommand,
        command_name: str,
        **kwargs: dict[str, Any],
    ) -> None:
        super().__init__(**kwargs)  # type: ignore[arg-type]
        parser = command.create_parser(command_name, "")

        # Put all the management command arguments on a list, skipping the ignored ones.
        action_list = [
            action
            for action in parser._actions  # noqa: SLF001
            if action.dest not in _IGNORED_ARGUMENT_NAMES
        ]

        # Add a field per store action
        for action in action_list:
            help_text = action.help or ""
            field: forms.Field = self._get_field(action, help_text)
            try:
                field_name = action.option_strings[0]
            except IndexError:
                field_name = f"___{action.dest}"

            field.label = action.dest
            field.required = action.required
            field.initial = action.default

            if field_name in self.fields:
                msg = (
                    f"{field_name} clashes with form field. Please rename {field_name}."
                )
                raise ValueError(msg)

            self.fields[field_name] = field

    def _get_field(
        self,
        action: argparse.Action,
        help_text: str,
    ) -> _Fields:
        field_type_mapping: dict[Any, type[_Fields]] = {
            "file": forms.FileField,
            "choices": forms.ChoiceField,
            date: forms.CharField,
            date_time: forms.CharField,
            int: forms.IntegerField,
            json_string: forms.CharField,
        }

        field_kwargs: dict[str, Any] = {"help_text": help_text}

        if action.type == json_string:
            field_kwargs["widget"] = forms.Textarea()
        elif action.type is bool:
            field_kwargs["choices"] = [(False, False), (True, True)]
            return field_type_mapping.get(action.dest, forms.ChoiceField)(
                **field_kwargs
            )
        elif action.choices:
            choices = [(str(c), str(c)) for c in action.choices]
            if not action.required:
                choices.insert(0, ("", "----------"))
            field_kwargs["choices"] = choices
            return field_type_mapping.get(action.dest, forms.ChoiceField)(
                **field_kwargs
            )

        return field_type_mapping.get(action.dest, forms.CharField)(**field_kwargs)

    def clean(self) -> dict[str, Any]:
        submitted_data = super().clean()
        cleaned_data = {}

        for field_name, field in self.fields.items():
            if not submitted_data:
                continue

            value = submitted_data[field_name]
            if not field.required and (value is None or value == ""):
                continue
            cleaned_data[field_name] = value

        return cleaned_data
