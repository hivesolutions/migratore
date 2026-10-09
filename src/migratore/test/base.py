#!/usr/bin/python
# -*- coding: utf-8 -*-

import legacy
import unittest

import migratore

from .mocks import FakeTable

try:
    import unittest.mock as mock
except ImportError:
    mock = None


class BaseTest(unittest.TestCase):
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        db = migratore.Migratore.get_test(strict=False)
        db.clear()

    def test_buffer(self):
        db = migratore.Database()
        buffer = db._buffer()
        buffer.write("select * from dummy")
        result = buffer.join()
        self.assertEqual(result, "select * from dummy")
        self.assertEqual(type(result), legacy.UNICODE)

    def test_create(self):
        db = migratore.Migratore.get_test()
        table = db.create_table("users")
        table.add_column("username", type="text")
        table.add_column("password", type="text")

        self.assertEqual(db.exists_table("users"), True)
        self.assertEqual(db.exists_table("users_extra"), False)
        self.assertEqual(table.has_column("username"), True)
        self.assertEqual(table.has_column("password"), True)
        self.assertEqual(table.type_column("username"), "longtext")
        self.assertEqual(table.type_column("password"), "longtext")

    def test_rename(self):
        db = migratore.Migratore.get_test()
        table = db.create_table("users")
        table.add_column("username", type="text")
        table.add_column("height", type="float")
        table.insert(username="11", height=42.84)
        table.change_column("username", "username_rename", type="integer")
        table.change_column("height", type="integer")

        self.assertEqual(table.has_column("username"), False)
        self.assertEqual(table.has_column("height"), True)
        self.assertEqual(table.has_column("username_rename"), True)
        self.assertEqual(table.type_column("username_rename"), "int")
        self.assertEqual(table.type_column("height"), "int")

        table = db.get_table("users")
        result = table.select(username_rename=11)
        self.assertNotEqual(len(result), 0)
        self.assertNotEqual(result[0], None)
        self.assertEqual(result[0]["username_rename"], 11)
        self.assertEqual(result[0]["height"], 43)
        self.assertEqual(type(result[0]["username_rename"]) in (int, legacy.LONG), True)
        self.assertEqual(type(result[0]["height"]) in (int, legacy.LONG), True)

    def test_create_index(self):
        db = migratore.Migratore.get_test()
        table = db.create_table("users")
        table.add_column("username", type="string")
        table.create_index("username")
        table.create_index("username", type="btree")

        self.assertEqual(table.has_index("username"), True)
        self.assertEqual(table.has_index("username", type="btree"), True)

        with self.assertRaises(Exception):
            table.create_index("username")

        self.assertEqual(table.has_index("username"), True)

    def test_drop_index(self):
        db = migratore.Migratore.get_test()
        table = db.create_table("users")
        table.add_column("username", type="string", index=True)
        table.add_column("email", type="string", index=True)
        table.drop_index("username")

        self.assertEqual(table.has_index("username"), False)
        self.assertEqual(table.has_index("username", type="btree"), True)
        self.assertEqual(table.has_index("email"), True)
        self.assertEqual(table.has_index("email", type="btree"), True)

        table.drop_index("username", type="btree")

        self.assertEqual(table.has_index("username", type="btree"), False)
        self.assertEqual(table.has_column("username"), True)

        with self.assertRaises(Exception):
            table.drop_index("username")

        table.create_index("username")

        self.assertEqual(table.has_index("username"), True)

    def test_drop_index_long(self):
        db = migratore.Migratore.get_test()
        table = db.create_table("users")
        name = "username_" + "a" * 51
        table.add_column(name, type="string", index=True)

        self.assertEqual(len("users_%s_hash" % name) > 64, True)
        self.assertEqual(table.has_index(name), True)
        self.assertEqual(table.has_index(name, type="btree"), True)

        table.drop_index(name)

        self.assertEqual(table.has_index(name), False)
        self.assertEqual(table.has_index(name, type="btree"), True)

    def test_has_index(self):
        db = migratore.Migratore.get_test()
        table = db.create_table("users")
        table.add_column("username", type="string")
        other = db.create_table("accounts")
        other.add_column("username", type="string", index=True)

        self.assertEqual(table.has_index("object_id"), True)
        self.assertEqual(table.has_index("object_id", type="btree"), True)
        self.assertEqual(table.has_index("username"), False)
        self.assertEqual(table.has_index("username", type="btree"), False)
        self.assertEqual(table.has_index("password"), False)
        self.assertEqual(other.has_index("username"), True)
        self.assertEqual(other.has_index("username", type="btree"), True)

        table.create_index("username")

        self.assertEqual(table.has_index("username"), True)
        self.assertEqual(table.has_index("username", type="btree"), False)

        table.add_foreign("account")

        self.assertEqual(table.has_index("account"), True)
        self.assertEqual(table.has_index("account", type="btree"), False)

    def test_environ_dot_env(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        mock_data = mock.mock_open(
            read_data=b"#This is a comment\nDB_PORT=80\nDB_USER=user\n"
        )

        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "builtins.open", mock_data, create=True
        ) as mock_open:
            args = []
            kwargs = {}
            migratore.Migratore._environ_dot_env(args, kwargs)

            result = kwargs["port"]
            self.assertEqual(type(result), int)
            self.assertEqual(result, 80)

            result = kwargs["username"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "user")

            self.assertEqual(len(kwargs), 2)

            self.assertEqual(mock_open.return_value.close.call_count, 1)

    def test__process_db_url(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        mock_data = mock.mock_open(
            read_data=b"DB_URL=mysql://root:pass@db.host:3000/db_name\n"
        )

        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "builtins.open", mock_data, create=True
        ) as mock_open:
            args = []
            kwargs = {}
            migratore.Migratore._environ_dot_env(args, kwargs)
            migratore.Migratore._process(args, kwargs)

            result = kwargs["db_url"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "mysql://root:pass@db.host:3000/db_name")

            result = kwargs["host"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "db.host")

            result = kwargs["port"]
            self.assertEqual(type(result), int)
            self.assertEqual(result, 3000)

            result = kwargs["username"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "root")

            result = kwargs["password"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "pass")

            result = kwargs["db"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "db_name")

            self.assertEqual(len(kwargs), 6)

            self.assertEqual(mock_open.return_value.close.call_count, 1)

    def test__process_db_url_defaults(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        mock_data = mock.mock_open(read_data=b"DB_URL=mysql://db.host/db_name\n")

        with mock.patch("os.path.exists", return_value=True), mock.patch(
            "builtins.open", mock_data, create=True
        ) as mock_open:
            args = []
            kwargs = {}
            migratore.Migratore._environ_dot_env(args, kwargs)
            migratore.Migratore._process(args, kwargs)

            result = kwargs["db_url"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "mysql://db.host/db_name")

            result = kwargs["host"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "db.host")

            result = kwargs["db"]
            self.assertEqual(type(result), str)
            self.assertEqual(result, "db_name")

            self.assertEqual(len(kwargs), 3)

            self.assertEqual(mock_open.return_value.close.call_count, 1)


class BaseMocksTest(unittest.TestCase):
    def test_exist_uuid_returns_false_for_nonexistent(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()

        with mock.patch.object(db, "get_table", return_value=FakeTable(records=[])):
            result = db.exist_uuid("nonexistent-uuid")
            self.assertEqual(result, False)

    def test_exist_uuid_returns_true_for_existing(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        def get_records(where):
            if "test-uuid" in where and "success" in where:
                return [{"uuid": "test-uuid", "result": "success"}]
            return []

        db = migratore.Database()

        with mock.patch.object(
            db, "get_table", return_value=FakeTable(records=get_records)
        ):
            result = db.exist_uuid("test-uuid")
            self.assertEqual(result, True)

    def test_exist_uuid_respects_result_parameter(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        def get_records(where):
            if "test-uuid" in where and "error" in where:
                return [{"uuid": "test-uuid", "result": "error"}]
            return []

        db = migratore.Database()

        with mock.patch.object(
            db, "get_table", return_value=FakeTable(records=get_records)
        ):
            result = db.exist_uuid("test-uuid")
            self.assertEqual(result, False)

            result = db.exist_uuid("test-uuid", result="error")
            self.assertEqual(result, True)

    def test_exist_uuid_handles_none_result(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()

        with mock.patch.object(db, "get_table", return_value=FakeTable(records=None)):
            result = db.exist_uuid("any-uuid")
            self.assertEqual(result, False)

    def test_is_applied_returns_false_for_nonexistent(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()

        with mock.patch.object(db, "get_table", return_value=FakeTable(records=None)):
            result = db.is_applied("any-uuid")
            self.assertEqual(result, False)

    def test_is_applied_returns_true_for_run(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()

        with mock.patch.object(
            db,
            "get_table",
            return_value=FakeTable(records={"operation": "Run"}),
        ):
            result = db.is_applied("test-uuid")
            self.assertEqual(result, True)

    def test_is_applied_returns_false_for_rollback(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()

        with mock.patch.object(
            db,
            "get_table",
            return_value=FakeTable(records={"operation": "Rollback"}),
        ):
            result = db.is_applied("test-uuid")
            self.assertEqual(result, False)

    def test_timestamp_returns_none_when_no_rows(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()

        with mock.patch.object(db, "get_table", return_value=FakeTable(records=[])):
            result = db.timestamp()
            self.assertEqual(result, None)

    def test_timestamp_returns_latest_for_run(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()
        rows = [
            {"uuid": "uuid-2", "operation": "Run", "timestamp": 2000},
            {"uuid": "uuid-1", "operation": "Run", "timestamp": 1000},
        ]

        with mock.patch.object(db, "get_table", return_value=FakeTable(records=rows)):
            result = db.timestamp()
            self.assertEqual(result, 2000)

    def test_timestamp_ignores_rolled_back_migrations(self):
        if mock == None:
            self.skipTest("Skipping test: mock unavailable")

        db = migratore.Database()
        rows = [
            {"uuid": "uuid-2", "operation": "Rollback", "timestamp": 2000},
            {"uuid": "uuid-2", "operation": "Run", "timestamp": 2000},
            {"uuid": "uuid-1", "operation": "Run", "timestamp": 1000},
        ]

        with mock.patch.object(db, "get_table", return_value=FakeTable(records=rows)):
            result = db.timestamp()
            self.assertEqual(result, 1000)

    def test_drop_index_ignored_for_base_table(self):
        db = migratore.Database()
        table = migratore.Table(db, "users")

        result = table.drop_index("username")
        self.assertEqual(result, None)

        result = table.drop_index("username", type="btree")
        self.assertEqual(result, None)
