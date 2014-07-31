#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import setuptools

BASE_PATH = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(BASE_PATH)
MIGRATORE_DIR = os.path.join(BASE_DIR, "src", "migratore")
sys.path.insert(0, MIGRATORE_DIR)

import info

setuptools.setup(
    name = info.NAME,
    version = info.VERSION,
    author = info.AUTHOR,
    author_email = info.EMAIL,
    description = info.DESCRIPTION,
    license = info.LICENSE,
    keywords = info.KEYWORDS,
    url = info.URL,
    zip_safe = True,
    packages = [
        "migratore",
        "migratore.examples",
        "migratore.examples.migrations"
    ],
    scripts = [
        "scripts/pypi/migratore",
        "scripts/pypi/migratore.bat",
        "scripts/pypi/migratore_pypi.py"
    ],
    package_dir = {
        "" : os.path.normpath("src")
    },
    package_data = {
        "migratore" : ["templates/*"]
    },
    entry_points = {
        "console_scripts" : [
            "migratore = migratore.cli:main"
        ]
    },
    classifiers = [
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7"
    ]
)
