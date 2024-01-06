#!/usr/bin/python
# -*- coding: utf-8 -*-

import legacy
import unittest

import migratore

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
