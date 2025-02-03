from unittest.mock import MagicMock, patch

from django.apps import apps
from django.conf import settings
from django.contrib.admin.sites import site
from django.contrib.auth.models import User
from django.test import RequestFactory, TestCase, override_settings
from django.urls import reverse

from django_command_form.models import CommandModel
from t.unit.admin import Command

DUMMY_APP_NAME = "t.unit"


@override_settings(
    INSTALLED_APPS=settings.INSTALLED_APPS + [DUMMY_APP_NAME]  # Add the dummy app label
)
class CommandAdminTestCase(TestCase):
    def setUp(self):
        self.admin = site._registry[Command]

        self.factory = RequestFactory()
        self.user = User.objects.create_user(username="testuser", password="password")
        self.user.is_superuser = True
        self.user.is_staff = True
        self.user.save()

    def test_dummy_app(self):
        self.assertIn(DUMMY_APP_NAME, [app.name for app in apps.get_app_configs()])

    @patch("django_command_form.admin.get_command_models")
    def test_changelist_view(self, mock_get_command_models):
        mock_get_command_models.return_value = [
            CommandModel(app_name="Unit", command_name="test_command")
        ]

        request = self.factory.get(reverse("admin:unit_command_changelist"))
        request.user = self.user
        response = self.admin.changelist_view(request)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Select command to execute", response.content.decode())

    @patch("django.core.management.base.BaseCommand", new_callable=MagicMock)
    @patch("django_command_form.admin.get_command_models")
    @patch("django_command_form.admin.get_command_contents")
    @patch("django_command_form.admin.management.get_commands")
    @patch("django_command_form.admin.management.load_command_class")
    def test_changeform_view_get(
        self,
        mock_load_command_class,
        mock_get_commands,
        mock_get_command_contents,
        mock_get_command_models,
        mock_base_command,
    ):
        # Make mock
        command_instance = mock_base_command.return_value
        command_instance.handle = MagicMock(return_value="Command executed")
        mock_load_command_class.return_value = command_instance

        mock_get_commands.return_value = {"test_command": "unit"}

        mock_get_command_contents.return_value = "Test Command Contents"

        mock_get_command_models.return_value = [
            CommandModel(app_name="Unit", command_name="test_command")
        ]

        mock_base_command.return_value.add_arguments = MagicMock()

        # Mock request and user
        request = self.factory.get(
            reverse("admin:unit_command_change", args=["test_command"])
        )
        request.user = self.user
        response = self.admin.changeform_view(request, object_id="test_command")

        # Assert the response
        self.assertEqual(response.status_code, 200)
        self.assertIn("Test Command Contents", response.content.decode())

    @patch("django_command_form.admin.CommandForm")
    @patch("django_command_form.admin.run_command")
    @patch("django_command_form.admin.get_command_models")
    @patch("django_command_form.admin.get_command_contents")
    @patch("django_command_form.admin.management.get_commands")
    @patch("django_command_form.admin.management.load_command_class")
    def test_changeform_view_post(
        self,
        mock_load_command_class,
        mock_get_commands,
        mock_get_command_contents,
        mock_get_command_models,
        mock_run_command,
        mock_command_form,
    ):
        mock_get_commands.return_value = {"test_command": "unit"}

        mock_get_command_contents.return_value = "Test Command Contents"

        mock_get_command_models.return_value = [
            CommandModel(app_name="Unit", command_name="test_command")
        ]

        command_instance = MagicMock()
        command_instance.help = "Test Command Help"
        mock_load_command_class.return_value = command_instance

        form_instance = MagicMock()
        form_instance.is_valid.return_value = True
        form_instance.cleaned_data = {"arg1": "value1"}
        mock_command_form.return_value = form_instance

        mock_run_command.return_value = "Command executed successfully"

        request = self.factory.post(
            reverse("admin:unit_command_change", args=["test_command"]),
            data={"arg1": "value1"},
        )
        request.user = self.user
        response = self.admin.changeform_view(request, object_id="test_command")

        self.assertEqual(response.status_code, 200)
        self.assertIn("Command executed successfully", response.content.decode())
