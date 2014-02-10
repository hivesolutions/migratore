#!/usr/bin/python
# -*- coding: utf-8 -*-

import time

import migratore

class Migration(migratore.Migration):

    def __init__(self):
        migratore.Migration.__init__(self)
        self.uuid = "b58707c9-48a7-46ff-ba38-474ee7c10d96"
        self.timestamp = 1392032961
        self.description = "adds new date field with current date"

    def run(self, db):
        migratore.Migration.run(self, db)

        table = db.get_table("users")

        self.begin("migrating schema")
        table.add_column("date", type = "integer")
        self.end("migrating schema")

        def task(value):
            _time = int(time.time())
            value.update(date = _time)

        table.apply(task, title = "creating dates")

migration = Migration()
