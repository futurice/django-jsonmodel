#!/usr/bin/env python
from setuptools import setup, find_packages, Command
from setuptools.command.test import test

import os, sys, subprocess

class TestCommand(Command):
    user_options = []

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        raise SystemExit(
            subprocess.call([sys.executable,
                             'app_test_runner.py',
                             'test']))

install_requires = [
    'djangorestframework>=3.3.2',
    'six',
]

setup(
    name = "django-jsonmodel",
    version = "0.0.10",
    description = "Convert Django Models to a JSON representation",
    url = "http://github.com/futurice-oss/django-jsonmodel",
    author = "Jussi Vaihia",
    author_email = "jussi.vaihia@futurice.com",
    packages = ["djangojsonmodel"],
    keywords = 'django json models js javascript',
    license = 'MIT',
    install_requires = install_requires,
    cmdclass = {
        'test': TestCommand,
    },
)
