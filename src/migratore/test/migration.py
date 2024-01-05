#!/usr/bin/python
# -*- coding: utf-8 -*-

import unittest

import migratore


class MigrationTest(unittest.TestCase):
    def test_order(self):
        migration_a = migratore.Migration(timestamp=2)
        migration_b = migratore.Migration(timestamp=1)
        migrations = [migration_a, migration_b]
        migrations.sort()
        self.assertEqual(migrations, [migration_b, migration_a])
