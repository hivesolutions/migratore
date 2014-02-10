#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

import base

class Loader(object):

    def __init__(self):
        self.migrations = []

    def load(self):
        return self.migrations

    def upgrade(self):
        migrations = self.load()

        db = base.Migratore.get_db()
        try:
            timestamp = db.timestamp()
            timestamp = timestamp or 0
            for migration in migrations:
                is_valid = migration.timestamp > timestamp
                if not is_valid: continue
                migration.start()
        finally: db.close()

class DirectoryLoader(Loader):

    def __init__(self, path):
        Loader.__init__(self)
        self.path = path

    def load(self):
        names = []
        modules = []

        sys.path.insert(0, self.path)

        files = os.listdir(self.path)

        for file in files:
            base, extension = os.path.splitext(file)
            if not extension == ".py": continue
            names.append(base)

        for name in names:
            module = __import__(name)
            modules.append(module)

        for module in modules:
            migration = getattr(module, "migration")
            self.migrations.append(migration)

        return self.migrations
