from setuptools import setup

setup(
    name="django-command-form",
    description=("A package that allows you to execute commands from DjangoAdmin."),
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="http://github.com/naohide/django-command-form/",
    license="MIT",
    author="naohide",
    author_email="n.anahara@fragment.co.jp",
    packages=["django_command_form"],
    include_package_data=True,
    version="0.0.5",
    install_requires=[
        "Django>=4.0",
    ],
)
