#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys
import setuptools

BASE_PATH = os.path.realpath(__file__)
BASE_DIR = os.path.dirname(BASE_PATH)
SRC_DIR = os.path.join(BASE_DIR, "src")
sys.path.insert(0, SRC_DIR)

import migratore

setuptools.setup(
    name = migratore.NAME,
    version = migratore.VERSION,
    author = migratore.AUTHOR,
    author_email = migratore.EMAIL,
    description = migratore.DESCRIPTION,
    license = migratore.LICENSE,
    keywords = migratore.KEYWORDS,
    url = migratore.URL,
    zip_safe = True,
    packages = [
        "migratore",
        "migratore.examples",
        "migratore.examples.migrations"
    ],
    test_suite = "migratore.test",
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
    install_requires = [
        "legacy"
    ],
    classifiers = [
        "Development Status :: 5 - Production/Stable",
        "Topic :: Utilities",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.0",
        "Programming Language :: Python :: 3.1",
        "Programming Language :: Python :: 3.2",
        "Programming Language :: Python :: 3.3",
        "Programming Language :: Python :: 3.4"
    ]
)
