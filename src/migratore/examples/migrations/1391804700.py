#!/usr/bin/python
# -*- coding: utf-8 -*-

import migratore


class Migration(migratore.Migration):
    def __init__(self):
        migratore.Migration.__init__(self)
        self.uuid = "e38376e1-c9ed-429b-a6f4-55b048c55d29"
        self.timestamp = 1391804700
        self.description = "adds the extra description column"

    def run(self, db):
        migratore.Migration.run(self, db)

        table = db.get_table("users")

        self.begin("migrating schema")
        table.add_column("description", type="text")
        self.end("migrating schema")

        def task(value):
            username = value["username"]
            description = "description-" + username
            value.update(description=description)

        table.apply(task, title="updating descriptions")

    def partial(self, db):
        migratore.Migration.partial(self, db)

        table = db.get_table("users")

        def task(value):
            username = value["username"]
            description = "description-" + username
            value.update(description=description)

        table.apply(task, title="updating descriptions")


migration = Migration()
