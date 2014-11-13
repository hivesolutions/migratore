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
