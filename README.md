[![Pypi Package](https://badge.fury.io/py/django-command-form.svg)](http://badge.fury.io/py/django-command-form)

### Django Command Form

This package allows you to execute commands from DjangoAdmin.

![Sample](https://i.imgur.com/Gwdf4CV.png)

#### Getting Started

```shell
$ pip install django-command-form
```

In your `settings.py`, add `django_command_form` to `INSTALLED_APPS`.

```python
INSTALLED_APPS = [
    ...
    'django_command_form',
]
```


In your `models.py`, create a class that inherits CommandModel.  
The class name is displayed as the name of the list in DjangoAdmin.

```python
from django_command_form.models import CommandModel


class Command(CommandModel):
    class Meta:
        proxy = True
```

Then, in `admin.py`, register the model with `CommandAdmin`.

```python
from django_command_form.admin import CommandAdmin


admin.site.register(Command, CommandAdmin)
```

### Compatible Django Version

| Compatible Django Version | Specifically tested |
| ------------------------- | ------------------- |
| `4.0`                     | :heavy_check_mark:  |
| `4.1`                     | :heavy_check_mark:  |
| `4.2`                     | :heavy_check_mark:  |
| `5.0`                     | :heavy_check_mark:  |
| `5.1`                     | :heavy_check_mark:  |