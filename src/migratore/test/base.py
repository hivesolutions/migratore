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
        db = self._get_db()
        if not db: return
        table = db.create_table("users")
        table.add_column("username", type = "text")
        table.add_column("password", type = "text")

    def _get_db(self):
        try: db = migratore.Migratore.get_db()
        except: db = None
        is_skip = not db and hasattr(self, "skipTest")
        if is_skip: self.skipTest("Not possible to access db")
        return db
