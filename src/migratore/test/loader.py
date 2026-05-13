#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import migratore

from .mocks import FakeDatabase, FakeMigration

try:
    import unittest.mock as mock
except ImportError:
    mock = None


class LoaderTest(unittest.TestCase):
    def test_dry_upgrade_filters_by_uuid(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)
        migration3 = FakeMigration("uuid-3", 3000)

        fake_db = FakeDatabase(existing_uuids={"uuid-2"})
        printed_migrations = []

        def capture_print(migration):
            printed_migrations.append(str(migration))

        with mock.patch.object(
            loader, "load", return_value=[migration1, migration2, migration3]
        ):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                with mock.patch("builtins.print", side_effect=capture_print):
                    loader.dry_upgrade()

        self.assertEqual(len(printed_migrations), 2)
        self.assertIn("Migration(uuid-1, 1000)", printed_migrations)
        self.assertIn("Migration(uuid-3, 3000)", printed_migrations)
        self.assertNotIn("Migration(uuid-2, 2000)", printed_migrations)

    def test_dry_upgrade_error_result_does_not_block(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 2000)

        fake_db = FakeDatabase(uuid_results={"uuid-1": "error"})
        printed_migrations = []

        def capture_print(migration):
            printed_migrations.append(str(migration))

        with mock.patch.object(loader, "load", return_value=[migration1]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                with mock.patch("builtins.print", side_effect=capture_print):
                    loader.dry_upgrade()

        self.assertEqual(len(printed_migrations), 1)
        self.assertIn("Migration(uuid-1, 2000)", printed_migrations)

    def test_downgrade_calls_rollback_when_implemented(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        class MigrationWithRollback(migratore.Migration):
            def rollback(self, db, force=False):
                pass

        loader = migratore.Loader()
        target = MigrationWithRollback(uuid="uuid-1", timestamp=1000)

        with mock.patch.object(loader, "get_last_migration", return_value=target):
            with mock.patch.object(target, "start") as mock_start:
                loader.downgrade()

        mock_start.assert_called_once_with(operation="rollback", force=True)

    def test_downgrade_raises_when_rollback_not_implemented(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        target = migratore.Migration(uuid="uuid-1", timestamp=1000)

        with mock.patch.object(loader, "get_last_migration", return_value=target):
            with self.assertRaises(RuntimeError) as context:
                loader.downgrade()

        self.assertIn("does not implement rollback", str(context.exception))

    def test_dry_downgrade_prints_last_migration(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        target = migratore.Migration(uuid="uuid-1", timestamp=1000)
        printed_migrations = []

        def capture_print(migration):
            printed_migrations.append(str(migration))

        with mock.patch.object(loader, "get_last_migration", return_value=target):
            with mock.patch("builtins.print", side_effect=capture_print):
                loader.dry_downgrade()

        self.assertEqual(len(printed_migrations), 1)
        self.assertIn("uuid-1", printed_migrations[0])

    def test_dry_downgrade_no_applied_raises(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()

        with mock.patch.object(loader, "load", return_value=[]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=FakeDatabase()
            ):
                with self.assertRaises(RuntimeError) as context:
                    loader.dry_downgrade()

        self.assertIn("No applied migration found", str(context.exception))

    def test_get_last_migration_returns_most_recent_applied(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)
        migration3 = FakeMigration("uuid-3", 3000)

        fake_db = FakeDatabase(existing_uuids={"uuid-1", "uuid-2"})

        with mock.patch.object(
            loader, "load", return_value=[migration1, migration2, migration3]
        ):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                result = loader.get_last_migration()

        self.assertEqual(result.uuid, "uuid-2")
        self.assertEqual(result.timestamp, 2000)

    def test_get_last_migration_no_applied_raises(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)

        fake_db = FakeDatabase()

        with mock.patch.object(loader, "load", return_value=[migration1]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                with self.assertRaises(RuntimeError) as context:
                    loader.get_last_migration()

        self.assertIn("No applied migration found", str(context.exception))
