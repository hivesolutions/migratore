#!/usr/bin/python
# -*- coding: utf-8 -*-

import migratore

def build(db):
    table = db.create_table("users")
    table.add_column("username", type = "text")

def cleanup(db):
    table = db.get_table("users")
    table.clear()

def data(db):
    table = db.get_table("users")
    for index in range(100):
        username = "username-" + str(index)
        table.insert(object_id = index, username = username)

def update(db):
    table = db.get_table("users")
    table.update({"username" : "new-0"}, username = "username-0")

def select(db):
    table = db.get_table("users")
    print table.count()
    print table.select(("object_id", "username"), username = "new-0")
    print table.get("object_id", username = "new-0", object_id = 0)

if __name__ == "__main__":
    loader = migratore.DirectoryLoader("C:/repo.extra/migratore/src/migratore/examples/migrations")
    loader.upgrade()

    #migration = TestMigration()
    #migration.start()

    #db = migratore.Migratore.get_db()
    #table = db.get_table("migratore")
    #print table.get()

    #db.names_table("migratore")
    #try:
    #    try: build(db)
    #    except: pass
    #    cleanup(db)
    #    data(db)
    #    update(db)
    #    select(db)
    #finally:
    #    db.close()

    # @todo tenho de implementar os indexex no add column

    # @todo tenho de criar a tabela migrations se nao tiver

    # @todo se tiver bulk operations por agulam informacao de progresso
    # e por isso com o \n
