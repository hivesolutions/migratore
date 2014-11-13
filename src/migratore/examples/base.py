#!/usr/bin/python
# -*- coding: utf-8 -*-

import os

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
    print(table.count())
    print(table.select(("object_id", "username"), username = "new-0"))
    print(table.get("object_id", username = "new-0", object_id = 0))

if __name__ == "__main__":
    file_path = os.path.abspath(__file__)
    dir_path = os.path.dirname(file_path)
    migrations_path = os.path.join(dir_path, "migrations")
    loader = migratore.DirectoryLoader(migrations_path)
    loader.upgrade()
