#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from . import base

class Loader(object):

    def __init__(self):
        self.migrations = []
        self.migrations_m = {}

    def __cmp__(self, value):
        return self.timestamp.__cmp__(value.timestamp)

    def __lt__(self, value):
        return self.timestamp < value.timestamp

    def __gt__(self, value):
        return self.timestamp > value.timestamp

    def __eq__(self, value):
        return self.timestamp == value.timestamp

    def __le__(self, value):
        return self.timestamp <= value.timestamp

    def __ge__(self, value):
        return self.timestamp >= value.timestamp

    def __ne__(self, value):
        return self.timestamp != value.timestamp

    def load(self):
        return self.migrations

    def upgrade(self, *args, **kwargs):
        migrations = self.load()

        db = base.Migratore.get_db(*args, **kwargs)
        try:
            timestamp = db.timestamp()
            timestamp = timestamp or 0
            for migration in migrations:
                is_valid = migration.timestamp > timestamp
                if not is_valid: continue
                result = migration.start()
                if not result == "success": break
        finally:
            db.close()

    def rebuild(self, id, *args, **kwargs):
        self.load()
        migration = self.migrations_m[id]
        migration.start(operation = "partial")

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
            if not hasattr(module, "migration"): continue
            migration = getattr(module, "migration")
            self.migrations.append(migration)
            self.migrations_m[migration.uuid] = migration
            self.migrations_m[str(migration.timestamp)] = migration

        self.migrations.sort(key = lambda item: item.timestamp)
        return self.migrations
