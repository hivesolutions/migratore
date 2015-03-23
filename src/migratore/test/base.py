#!/usr/bin/python
# -*- coding: utf-8 -*-

import legacy
import unittest

import migratore

class BaseTest(unittest.TestCase):

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        db = migratore.Migratore.get_test(strict = False)
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
        table.add_column("username", type = "text")
        table.add_column("password", type = "text")

        self.assertEqual(db.exists_table("users"), True)
        self.assertEqual(db.exists_table("users_extra"), False)
        self.assertEqual(table.has_column("username"), True)
        self.assertEqual(table.has_column("password"), True)
        self.assertEqual(table.type_column("username"), "longtext")
        self.assertEqual(table.type_column("password"), "longtext")

    def test_rename(self):
        db = migratore.Migratore.get_test()
        table = db.create_table("users")
        table.add_column("username", type = "text")
        table.add_column("height", type = "float")
        table.insert(username = "11", height = 42.84)
        table.change_column("username", "username_rename", type = "integer")
        table.change_column("height", "height_rename", type = "integer")

        self.assertEqual(table.has_column("username"), False)
        self.assertEqual(table.has_column("height"), False)
        self.assertEqual(table.has_column("username_rename"), True)
        self.assertEqual(table.has_column("height_rename"), True)
        self.assertEqual(table.type_column("username_rename"), "int")
        self.assertEqual(table.type_column("height_rename"), "int")

        table = db.get_table("users")
        result = table.select(username_rename = 11)
        self.assertNotEqual(len(result), 0)
        self.assertNotEqual(result[0], None)
        self.assertEqual(result[0]["username_rename"], 11)
        self.assertEqual(result[0]["height_rename"], 43)
        self.assertEqual(type(result[0]["username_rename"]), long)
        self.assertEqual(type(result[0]["height_rename"]), long)
