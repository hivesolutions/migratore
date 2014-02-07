#!/usr/bin/python
# -*- coding: utf-8 -*-

import migratore

def build(db):
    db = migratore.Migratore.get_db()
    table = db.create_table("users")
    table.add_column("username", type = "text")

def cleanup(db):
    db = migratore.Migratore.get_db()
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
    db = migratore.Migratore.get_db()
    try:
        try: build(db)
        except: pass
        cleanup(db)
        data(db)
        update(db)
        select(db)
    finally:
        db.close()



    # @todo se tiver bulk operations por agulam informacao de progresso
    # e por isso com o \n
