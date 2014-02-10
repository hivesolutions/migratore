#!/usr/bin/python
# -*- coding: utf-8 -*-

import migratore

class Migration(migratore.Migration):

    def __init__(self):
        migratore.Migration.__init__(self)
        self.uuid = "%s"
        self.timestamp = %d
        self.description = "%s"

    def run(self, db):
        migratore.Migration.run(self, db)

migration = Migration()
