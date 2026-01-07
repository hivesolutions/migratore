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

    def test_dry_upgrade_filters_by_timestamp(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)
        migration3 = FakeMigration("uuid-3", 3000)

        fake_db = FakeDatabase(current_timestamp=2000)
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

        self.assertEqual(len(printed_migrations), 1)
        self.assertIn("Migration(uuid-3, 3000)", printed_migrations)

    def test_dry_upgrade_filters_by_both_uuid_and_timestamp(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 3000)
        migration3 = FakeMigration("uuid-3", 4000)

        fake_db = FakeDatabase(current_timestamp=2000, existing_uuids={"uuid-2"})
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

        self.assertEqual(len(printed_migrations), 1)
        self.assertIn("Migration(uuid-3, 4000)", printed_migrations)

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
