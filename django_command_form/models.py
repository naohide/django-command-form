from __future__ import annotations

from django.db import models
from django.utils.translation import gettext_lazy as _


class CommandModel(models.Model):
    app_name: models.CharField[str, str] = models.CharField(
        verbose_name=_("App Name"),
        max_length=255,
        help_text=_("The apps that are defined in the system"),
    )
    command_name: models.CharField[str, str] = models.CharField(
        primary_key=True,
        verbose_name=_("Command Name"),
        max_length=255,
        help_text=_("The commands that are defined in the system"),
    )

    class Meta:
        managed = False
        verbose_name = _("command")
        verbose_name_plural = _("commands")

    def __str__(self) -> str:
        return f"{self.command_name}"
