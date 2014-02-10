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

        table.remove_column("description")
        table.add_column("description", type = "text")

        self.end("migrating schema")

        def generator(value):
            username = value["username"]
            description = "description-" + username
            value.update(description = description)

        table.apply(generator, title = "updating descriptions")

        # @todo ainda faltam os indices

migration = Migration()
