import os
import io

from setuptools import setup, find_packages

NAME = "aviary"
DESCRIPTION = "Air traffic scenario generation for the Simurgh project."
URL = "https://github.com/alan-turing-institute/aviary"
AUTHOR = "Tim Hobson and Radka Jersakova"
EMAIL = "thobson@turing.ac.uk"
REQUIRES_PYTHON = ">=3.6.0"
VERSION = None
LICENSE = "MIT"

REQUIRED = ["Shapely==1.6.*"]

EXTRAS = {
    "docs": ["sphinx"],
    "tests": ["pytest"],
    "dev": ["sphinx", "pytest"]
}

here = os.path.abspath(os.path.dirname(__file__))

try:
    with io.open(os.path.join(here, "README.md"), encoding="utf-8") as f:
        long_description = "\n" + f.read()
except FileNotFoundError:
    long_description = DESCRIPTION

# TODO: load package's version from __version__.py module

setup(
    name=NAME,
    version=VERSION,
    description=DESCRIPTION,
    long_description=long_description,
    long_description_concent_type="text/markdown",
    author=AUTHOR,
    author_email=EMAIL,
    python_requires=REQUIRES_PYTHON,
    url=URL,
    packages=find_packages(
        exclude=["tests", "*.tests", "*.tests.*", "tests.*"]
    ),
    install_requires=REQUIRED,
    extras_require=EXTRAS,
    include_package_data=True, # include items specified in MANIFEST.in
    license=LICENSE
)
