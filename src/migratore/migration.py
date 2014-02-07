#!/usr/bin/python
# -*- coding: utf-8 -*-

import base

class Migration(object):

    def __init__(self):
        self.uuid = None
        self.name = None
        self.description = None

    def start(self):
        db = base.Migratore.get_db()
        self.run(db)

    def run(self, db):
        raise RuntimeError("Not implemented")
