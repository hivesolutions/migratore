#!/usr/bin/python
# -*- coding: utf-8 -*-

import migratore

class Migration(migratore.Migration):

    def __init__(self):
        migratore.Migration.__init__(self)
        self.uuid = "59a287c0-36a5-4dd7-898b-b421d3ea8d81"
        self.timestamp = 1391804600
        self.description = "initial setup and provision of the database"

    def run(self, db):
        migratore.Migration.run(self, db)

        self.begin("creating schema")
        table = db.create_table("users")
        table.add_column("username", type = "text")
        table.add_column("password", type = "text")
        self.end("creating schema")

        def task(table, index):
            object_id = index + 1
            username = "username-%d" % object_id
            password = "password-%d" % object_id
            table.insert(
                object_id = object_id,
                username = username,
                password = password
            )

        table.run(task, 1000, title = "provisioning schema")

migration = Migration()
