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
    def test_upgrade_runs_migrations_after_last_applied(self):
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
                loader.upgrade()

        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, None)
        self.assertEqual(migration3.started_operation, "run")
        self.assertEqual(fake_db.closed, True)

    def test_upgrade_runs_all_when_none_applied(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)

        fake_db = FakeDatabase()

        with mock.patch.object(loader, "load", return_value=[migration1, migration2]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                loader.upgrade()

        self.assertEqual(migration1.started_operation, "run")
        self.assertEqual(migration2.started_operation, "run")
        self.assertEqual(fake_db.closed, True)

    def test_upgrade_is_noop_when_all_applied(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)

        fake_db = FakeDatabase(existing_uuids={"uuid-1", "uuid-2"})

        with mock.patch.object(loader, "load", return_value=[migration1, migration2]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                loader.upgrade()

        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, None)
        self.assertEqual(fake_db.closed, True)

    def test_upgrade_reruns_errored_migration(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)

        fake_db = FakeDatabase(uuid_results={"uuid-1": "success", "uuid-2": "error"})

        with mock.patch.object(loader, "load", return_value=[migration1, migration2]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                loader.upgrade()

        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, "run")

    def test_upgrade_raises_on_failed_migration(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000, result="error")
        migration3 = FakeMigration("uuid-3", 3000)

        fake_db = FakeDatabase(existing_uuids={"uuid-1"})

        with mock.patch.object(
            loader, "load", return_value=[migration1, migration2, migration3]
        ):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                with self.assertRaises(RuntimeError) as context:
                    loader.upgrade()

        self.assertIn("Migration 'uuid-2' failed", str(context.exception))
        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, "run")
        self.assertEqual(migration3.started_operation, None)
        self.assertEqual(fake_db.closed, True)

    def test_dry_upgrade_prints_migrations_after_last_applied(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)
        migration3 = FakeMigration("uuid-3", 3000)

        fake_db = FakeDatabase(existing_uuids={"uuid-1", "uuid-2"})
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

    def test_dry_upgrade_prints_all_when_none_applied(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)

        fake_db = FakeDatabase()
        printed_migrations = []

        def capture_print(migration):
            printed_migrations.append(str(migration))

        with mock.patch.object(loader, "load", return_value=[migration1, migration2]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                with mock.patch("builtins.print", side_effect=capture_print):
                    loader.dry_upgrade()

        self.assertEqual(len(printed_migrations), 2)
        self.assertIn("Migration(uuid-1, 1000)", printed_migrations)
        self.assertIn("Migration(uuid-2, 2000)", printed_migrations)

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

    def test_mark_records_run_skip_for_each_pending(self):
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)
        migration3 = FakeMigration("uuid-3", 3000)

        loader = migratore.Loader()
        loader.migrations = [migration1, migration2, migration3]

        fake_db = FakeDatabase(existing_uuids={"uuid-1"})
        try:
            migratore.base.Migratore._database = fake_db
            loader.mark()
        finally:
            migratore.base.Migratore.invalidate()

        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, "run_skip")
        self.assertEqual(migration3.started_operation, "run_skip")

    def test_mark_records_run_skip_for_all_when_none_applied(self):
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)

        loader = migratore.Loader()
        loader.migrations = [migration1, migration2]

        fake_db = FakeDatabase()
        try:
            migratore.base.Migratore._database = fake_db
            loader.mark()
        finally:
            migratore.base.Migratore.invalidate()

        self.assertEqual(migration1.started_operation, "run_skip")
        self.assertEqual(migration2.started_operation, "run_skip")

    def test_mark_is_noop_when_all_applied(self):
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)

        loader = migratore.Loader()
        loader.migrations = [migration1, migration2]

        fake_db = FakeDatabase(existing_uuids={"uuid-1", "uuid-2"})
        try:
            migratore.base.Migratore._database = fake_db
            loader.mark()
        finally:
            migratore.base.Migratore.invalidate()

        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, None)

    def test_mark_raises_on_failed_migration(self):
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000, result="error")
        migration3 = FakeMigration("uuid-3", 3000)

        loader = migratore.Loader()
        loader.migrations = [migration1, migration2, migration3]

        fake_db = FakeDatabase(existing_uuids={"uuid-1"})
        try:
            migratore.base.Migratore._database = fake_db
            with self.assertRaises(RuntimeError) as context:
                loader.mark()
        finally:
            migratore.base.Migratore.invalidate()

        self.assertIn("Migration 'uuid-2' failed", str(context.exception))
        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, "run_skip")
        self.assertEqual(migration3.started_operation, None)
        self.assertEqual(fake_db.closed, True)

    def test_downgrade_calls_rollback_when_implemented(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        class MigrationWithRollback(migratore.Migration):
            def rollback(self, db, force=False):
                pass

        loader = migratore.Loader()
        target = MigrationWithRollback(uuid="uuid-1", timestamp=1000)

        with mock.patch.object(loader, "get_last_migration", return_value=target):
            with mock.patch.object(
                target, "start", return_value="success"
            ) as mock_start:
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

    def test_downgrade_raises_on_failed_rollback(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        class MigrationWithRollback(migratore.Migration):
            def rollback(self, db, force=False):
                pass

        loader = migratore.Loader()
        target = MigrationWithRollback(uuid="uuid-1", timestamp=1000)

        with mock.patch.object(loader, "get_last_migration", return_value=target):
            with mock.patch.object(target, "start", return_value="error") as mock_start:
                with self.assertRaises(RuntimeError) as context:
                    loader.downgrade()

        mock_start.assert_called_once_with(operation="rollback", force=True)
        self.assertIn("Migration 'uuid-1' failed", str(context.exception))

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

    def test_rebuild_runs_partial_on_migration(self):
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)

        loader = migratore.Loader()
        loader.migrations_m = {"uuid-1": migration1, "uuid-2": migration2}

        loader.rebuild("uuid-2")

        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, "run_partial")

    def test_rebuild_raises_on_failed_migration(self):
        migration1 = FakeMigration("uuid-1", 1000, result="error")

        loader = migratore.Loader()
        loader.migrations_m = {"uuid-1": migration1}

        with self.assertRaises(RuntimeError) as context:
            loader.rebuild("uuid-1")

        self.assertIn("Migration 'uuid-1' failed", str(context.exception))
        self.assertEqual(migration1.started_operation, "run_partial")

    def test_rebuild_not_found_raises(self):
        loader = migratore.Loader()
        loader.migrations_m = {"uuid-1": FakeMigration("uuid-1", 1000)}

        with self.assertRaises(RuntimeError) as context:
            loader.rebuild("uuid-x")

        self.assertIn("Migration 'uuid-x' not found", str(context.exception))

    def test_skip_runs_skip_on_current_migration(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000)
        migration2 = FakeMigration("uuid-2", 2000)
        migration3 = FakeMigration("uuid-3", 3000)

        fake_db = FakeDatabase(existing_uuids={"uuid-1"})

        with mock.patch.object(
            loader, "load", return_value=[migration1, migration2, migration3]
        ):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                loader.skip()

        self.assertEqual(migration1.started_operation, None)
        self.assertEqual(migration2.started_operation, "run_skip")
        self.assertEqual(migration3.started_operation, None)

    def test_skip_raises_on_failed_migration(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        loader = migratore.Loader()
        migration1 = FakeMigration("uuid-1", 1000, result="error")

        fake_db = FakeDatabase()

        with mock.patch.object(loader, "load", return_value=[migration1]):
            with mock.patch.object(
                migratore.base.Migratore, "get_db", return_value=fake_db
            ):
                with self.assertRaises(RuntimeError) as context:
                    loader.skip()

        self.assertIn("Migration 'uuid-1' failed", str(context.exception))
        self.assertEqual(migration1.started_operation, "run_skip")

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
