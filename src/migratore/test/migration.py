#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import re
import shutil
import tempfile
import unittest

import migratore


class MigrationTest(unittest.TestCase):
    def test_order(self):
        migration_a = migratore.Migration(timestamp=2)
        migration_b = migratore.Migration(timestamp=1)
        migrations = [migration_a, migration_b]
        migrations.sort()
        self.assertEqual(migrations, [migration_b, migration_a])

    def test_safe_rollback(self):
        """
        Tests that `SAFE` config variable controls the rollback
        behavior of the `Migration` class.

        If `SAFE` is `True`, the database will be rolled back if an
        exception is raised.

        If `SAFE` is `False`, the rollback will be handled by the
        `rollback` method of the `Migration` class.
        """

        # fake database to track rollback calls
        class FakeDatabase(object):
            def __init__(self, safe):
                self.safe = safe
                self.db_rollback_called = False
                self.commit_called = False

            def rollback(self):
                self.db_rollback_called = True

            def commit(self):
                self.commit_called = True

            def get_table(self, name):
                return FakeTable()

        class FakeTable(object):
            def insert(self, **kwargs):
                pass

        # migration that raises an exception
        class FailingMigration(migratore.Migration):
            def __init__(self):
                migratore.Migration.__init__(
                    self,
                    uuid="test-uuid",
                    timestamp=1234567890,
                    description="Test migration that fails",
                )
                self.rollback_called = False

            def run(self, db):
                raise RuntimeError("Test exception")

            def rollback(self, db):
                self.rollback_called = True
                migratore.Migration.rollback(self, db)

            def cleanup(self, db):
                pass

        # safe=True should call db.rollback()
        migration_safe = FailingMigration()
        fake_db_safe = FakeDatabase(safe=True)

        result = migration_safe._start(fake_db_safe, "run", "test")

        self.assertTrue(fake_db_safe.db_rollback_called)
        self.assertFalse(migration_safe.rollback_called)
        self.assertEqual(result, "error")
        self.assertTrue(fake_db_safe.commit_called)

        # safe=False should call self.rollback(db)
        migration_unsafe = FailingMigration()
        fake_db_unsafe = FakeDatabase(safe=False)

        result_unsafe = migration_unsafe._start(fake_db_unsafe, "run", "test")

        self.assertTrue(migration_unsafe.rollback_called)
        self.assertEqual(result_unsafe, "error")
        self.assertTrue(fake_db_unsafe.commit_called)

    def test_touch(self):
        temp_dir = tempfile.mkdtemp()
        try:
            old_timestamp = 1391804600
            migration_content = (
                """#!/usr/bin/python
# -*- coding: utf-8 -*-

import migratore

class Migration(migratore.Migration):
    def __init__(self):
        migratore.Migration.__init__(self)
        self.uuid = "test-uuid"
        self.timestamp = %d
        self.description = "test migration"

migration = Migration()
"""
                % old_timestamp
            )

            old_path = os.path.join(temp_dir, "%d.py" % old_timestamp)
            with open(old_path, "wb") as file:
                file.write(migration_content.encode("utf-8"))

            migratore.Migration.touch_file(old_path)

            self.assertFalse(os.path.exists(old_path))

            files = os.listdir(temp_dir)
            self.assertEqual(len(files), 1)

            new_filename = files[0]
            self.assertTrue(new_filename.endswith(".py"))
            new_timestamp = int(new_filename[:-3])
            self.assertGreater(new_timestamp, old_timestamp)

            new_path = os.path.join(temp_dir, new_filename)
            with open(new_path, "rb") as file:
                new_content = file.read().decode("utf-8")

            match = re.search(r"self\.timestamp\s*=\s*(\d+)", new_content)
            self.assertIsNotNone(match)
            self.assertEqual(int(match.group(1)), new_timestamp)
        finally:
            shutil.rmtree(temp_dir)
