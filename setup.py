import os
from setuptools import setup

install_requires = []
base_dir = os.path.dirname(os.path.abspath(__file__))

setup(
    name = "django-jsonmodel",
    version = "0.0.6",
    description = "Convert Django model structure into a JSON representation for client-side applications",
    url = "http://github.com/futurice-oss/django-jsonmodel",
    author = "Jussi Vaihia",
    author_email = "jussi.vaihia@futurice.com",
    packages = ["djangojsonmodel"],
    keywords = 'django json models js javascript',
    license = 'MIT',
    install_requires = install_requires,
    #test_suite = "tests.tests",
)
