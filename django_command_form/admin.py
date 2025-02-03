from __future__ import annotations

from typing import Any

from django.contrib import admin
from django.contrib.admin import helpers
from django.contrib.admin.helpers import AdminForm
from django.contrib.admin.views.main import ChangeList
from django.core import management
from django.http.request import HttpRequest
from django.http.response import HttpResponse
from django.shortcuts import render
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from .command import get_command_contents, get_command_models, run_command
from .forms import CommandForm
from .models import CommandModel


class CommandChangeList(ChangeList):
    def get_queryset(  # type: ignore[override]
        self,
        request: HttpRequest,  # noqa: ARG002
        exclude_parameters: list[str] | None = None,  # noqa: ARG002
    ) -> list[CommandModel]:
        return get_command_models(self.model._meta.app_label)  # noqa: SLF001

    def get_results(self, request: HttpRequest) -> None:
        self.result_list = self.get_queryset(request)
        self.full_result_count = len(self.result_list)
        self.result_count = self.full_result_count
        self.can_show_all = True
        self.multi_page = False
        self.formset = None
        self.show_admin_actions = False

    @property
    def action_form(self) -> helpers.ActionForm:
        return helpers.ActionForm()


class CommandAdmin(admin.ModelAdmin):  # type: ignore[type-arg]
    def has_add_permission(self, request: HttpRequest) -> bool:  # noqa: ARG002
        return False

    def has_change_permission(
        self,
        request: HttpRequest,  # noqa: ARG002
        obj: CommandModel | None = None,  # noqa: ARG002
    ) -> bool:
        return False

    def has_delete_permission(
        self,
        request: HttpRequest,  # noqa: ARG002
        obj: CommandModel | None = None,  # noqa: ARG002
    ) -> bool:
        return False

    def changelist_view(
        self,
        request: HttpRequest,
        extra_context: dict[str, Any] | None = None,
    ) -> HttpResponse:
        change_list = CommandChangeList(
            request,
            self.model,
            date_hierarchy=None,
            model_admin=self,
            list_display=self.list_display,
            list_display_links=self.list_display_links,  # type: ignore[arg-type]
            list_editable=(),
            list_filter=(),
            list_max_show_all=1000,
            list_per_page=1000,
            list_select_related=(),
            search_fields=(),
            search_help_text=None,
            sortable_by=None,
        )

        change_list.queryset = change_list.get_queryset(request)

        context = {
            **self.admin_site.each_context(request),
            "cl": change_list,
            "opts": self.model._meta,  # noqa: SLF001
            "action_form": change_list.action_form,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "actions_on_top": self.actions_on_top,
            "actions_on_bottom": self.actions_on_bottom,
            "has_add_permission": False,
            "has_change_permission": self.has_change_permission(request),
            "has_delete_permission": False,
            "has_view_permission": self.has_view_permission(request),
            "title": _("Select command to execute"),
            "subtitle": "",
            "original": "",
            "media": self.media,
            **(extra_context or {}),
        }
        return render(request, "admin/change_list.html", context)

    def changeform_view(
        self,
        request: HttpRequest,
        object_id: str | None = None,
        form_url: str = "",  # noqa: ARG002
        extra_context: dict[str, Any] | None = None,  # noqa: ARG002
    ) -> HttpResponse:
        commands = get_command_models(self.model._meta.app_label)  # noqa: SLF001
        command = next(
            (c for c in commands if c.command_name == object_id.replace("_5F", "_")),
            None,
        )
        if not command:
            msg = f"Command {object_id} not found"
            raise ValueError(msg)

        app_name = management.get_commands()[command.command_name]
        cls = management.load_command_class(app_name, command.command_name)
        if request.method == "POST":
            form = CommandForm(cls, command.command_name, data=request.POST)
        else:
            form = CommandForm(cls, command.command_name)

        admin_form = AdminForm(
            form,  # type: ignore[arg-type]
            fieldsets=[(None, {"fields": form.fields.keys()})],  # type: ignore[dict-item]
            prepopulated_fields={},
            readonly_fields=(),
            model_admin=self,
        )

        context = {
            **self.admin_site.each_context(request),
            "adminform": admin_form,
            "opts": self.model._meta,  # noqa: SLF001
            "add": False,
            "change": False,
            "save_as": False,
            "save_on_top": False,
            "to_field": None,
            "has_permission": True,
            "has_add_permission": False,
            "has_change_permission": self.has_change_permission(request),
            "has_delete_permission": False,
            "has_view_permission": self.has_view_permission(request),
            "has_editable_inline_admin_formsets": False,
            "has_file_field": False,
            "has_absolute_url": False,
            "inline_admin_formsets": [],
            "title": command.command_name,
            "subtitle": cls.help,
            "original": command.command_name.title(),
            "absolute_url": None,
            "form_url": "",
            "changelist_url": reverse(
                f"admin:{self.opts.app_label}_{self.opts.model_name}_changelist"
            ),
            "media": self.media + admin_form.media,
            "contents": get_command_contents(app_name, command.command_name),
            "errors": [],
        }

        if request.method == "POST":
            if form.is_valid():
                context["message"] = run_command(
                    command.command_name,
                    form.cleaned_data,
                )
                return render(request, "command/exec_done.html", context)
            context["errors"] = form.errors
        return render(request, "command/exec_form.html", context)
