from django.contrib import admin

from django_command_form.admin import CommandAdmin
from django_command_form.models import CommandModel


class Command(CommandModel):
    class Meta:
        proxy = True
        app_label = "unit"  # Specify a dummy app label for the test


admin.site.register(Command, CommandAdmin)
