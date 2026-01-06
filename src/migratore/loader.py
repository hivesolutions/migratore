#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

from . import base


class Loader(object):
    def __init__(self):
        self.migrations = []
        self.migrations_m = {}
        self.migrations_path = {}

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
                if not is_valid:
                    continue
                result = migration.start()
                if not result == "success":
                    break
        finally:
            db.close()

    def dry_upgrade(self, *args, **kwargs):
        migrations = self.load()

        db = base.Migratore.get_db(*args, **kwargs)
        try:
            timestamp = db.timestamp()
            timestamp = timestamp or 0
            for migration in migrations:
                is_valid = migration.timestamp > timestamp
                if not is_valid:
                    continue
                print(migration)
        finally:
            db.close()

    def rebuild(self, id, *args, **kwargs):
        self.load()
        migration = self.migrations_m[id]
        if not migration:
            raise RuntimeError("Migration '%s' not found" % id)
        migration.start(operation="run_partial")

    def touch(self, id, *args, **kwargs):
        from . import migration

        self.load()
        path = self.migrations_path.get(id)
        if not path:
            raise RuntimeError("Migration '%s' not found" % id)
        migration.Migration.touch_file(path)

    def skip(self, *args, **kwargs):
        migration = self.get_current_migration()
        migration.start(operation="run_skip")

    def get_current_migration(self):
        migrations = self.load()

        db = base.Migratore.get_db()
        try:
            timestamp = db.timestamp()
            timestamp = timestamp or 0
            for migration in migrations:
                if migration.timestamp > timestamp:
                    return migration
        finally:
            db.close()

        raise RuntimeError("No current migration found")

    def get_migration(self, timestamp):
        migrations = self.load()
        for migration in migrations:
            if migration.timestamp == timestamp:
                return migration
        raise RuntimeError("No migration found for timestamp %d" % timestamp)

    def get_migration_by_uuid(self, uuid):
        migrations = self.load()
        for migration in migrations:
            if migration.uuid == uuid:
                return migration
        raise RuntimeError("No migration found for UUID %s" % uuid)

    def get_migration_by_any(self, timestamp_or_uuid):
        migrations = self.load()
        for migration in migrations:
            if migration.timestamp == timestamp_or_uuid:
                return migration
            if migration.uuid == timestamp_or_uuid:
                return migration
        raise RuntimeError(
            "No migration found for identifier %s" % str(timestamp_or_uuid)
        )


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
            if not extension == ".py":
                continue
            names.append((base, file))

        for name, file in names:
            module = __import__(name)
            modules.append((module, file))

        for module, file in modules:
            if not hasattr(module, "migration"):
                continue
            migration = getattr(module, "migration")
            self.migrations.append(migration)
            self.migrations_m[migration.uuid] = migration
            self.migrations_m[str(migration.timestamp)] = migration
            self.migrations_path[migration.uuid] = os.path.join(self.path, file)
            self.migrations_path[str(migration.timestamp)] = os.path.join(
                self.path, file
            )

        self.migrations.sort(key=lambda item: item.timestamp)
        return self.migrations
