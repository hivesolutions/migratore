#!/usr/bin/python
# -*- coding: utf-8 -*-

import legacy
import unittest

import migratore

class BaseTest(unittest.TestCase):

    def test_buffer(self):
        db = migratore.Database(None, None)
        buffer = db._buffer()
        buffer.write("select * from dummy")
        result = buffer.join()
        self.assertEqual(result, "select * from dummy")
        self.assertEqual(type(result), legacy.UNICODE)

    def test_create(self):
        db = migratore.Migratore.get_db()
        table = db.create_table("users")
        table.add_column("username", type = "text")
        table.add_column("password", type = "text")

        self.assertEqual(db.exists_table("users"), True)
        self.assertEqual(db.exists_table("users_extra"), False)
        self.assertEqual(table.has_column("username"), True)
        self.assertEqual(table.has_column("password"), True)
        self.assertEqual(table.type_column("username"), "longtext")
        self.assertEqual(table.type_column("password"), "longtext")
