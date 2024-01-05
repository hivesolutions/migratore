#!/usr/bin/python
# -*- coding: utf-8 -*-

from . import base


class MySQLDatabase(base.Database):
    def __init__(self, *args, **kwargs):
        base.Database.__init__(self, *args, **kwargs)
        self.engine = "mysql"
        self.isolation_level = "read committed"

    def open(self):
        base.Database.open(self)
        buffer = self._buffer()
        buffer.write("set session transaction isolation level ")
        buffer.write(self.isolation_level)
        buffer.execute()

    def table(self, *args, **kwargs):
        return MySQLTable(*args, **kwargs)

    def count_tables(self):
        buffer = self._buffer()
        buffer.write("select count(*) ")
        buffer.write("from information_schema.tables where table_schema = '")
        buffer.write(self.name)
        buffer.write("'")
        counts = buffer.execute(fetch=True)
        return counts[0][0]

    def exists_table(self, name):
        buffer = self._buffer()
        buffer.write("select count(*) ")
        buffer.write("from information_schema.tables where table_schema = '")
        buffer.write(self.name)
        buffer.write("' and table_name = '")
        buffer.write(name)
        buffer.write("'")
        counts = buffer.execute(fetch=True)
        exists = True if counts and counts[0][0] > 0 else False
        return exists

    def names_table(self, name):
        buffer = self._buffer()
        buffer.write("select column_name ")
        buffer.write("from information_schema.columns where table_schema = '")
        buffer.write(self.name)
        buffer.write("' and table_name = '")
        buffer.write(name)
        buffer.write("'")
        names = buffer.execute(fetch=True)
        names = [value[0] for value in names]
        return names

    def _apply_types(self):
        base.Database._apply_types(self)
        self.types_map["text"] = "longtext"
        self.types_map["data"] = "longtext"
        self.types_map["metadata"] = "longtext"


class MySQLTable(base.Table):
    def create_index(self, name, type="hash"):
        index = "%s_%s_%s" % (self.name, name, type)
        index = index[-64:]
        buffer = self.owner._buffer()
        buffer.write("create index ")
        buffer.write(index)
        buffer.write(" on ")
        buffer.write(self.name)
        buffer.write("(")
        buffer.write(name)
        buffer.write(") using ")
        buffer.write(type)
        buffer.execute()

    def drop_index(self, name):
        index = "%s_%s_%s" % (self.name, name, type)
        index = index[-64:]
        buffer = self.owner._buffer()
        buffer.write("drop index ")
        buffer.write(index)
        buffer.write(" on ")
        buffer.write(self.name)
        buffer.execute()

    def has_column(self, name):
        buffer = self.owner._buffer()
        buffer.write("select count(*) ")
        buffer.write("from information_schema.columns where table_schema = '")
        buffer.write(self.owner.name)
        buffer.write("' and table_name = '")
        buffer.write(self.name)
        buffer.write("' and column_name = '")
        buffer.write(name)
        buffer.write("'")
        counts = buffer.execute(fetch=True)
        exists = True if counts and counts[0][0] > 0 else False
        return exists

    def type_column(self, name):
        buffer = self.owner._buffer()
        buffer.write("select data_type ")
        buffer.write("from information_schema.columns where table_schema = '")
        buffer.write(self.owner.name)
        buffer.write("' and table_name = '")
        buffer.write(self.name)
        buffer.write("' and column_name = '")
        buffer.write(name)
        buffer.write("'")
        result = buffer.execute(fetch=True)
        return result[0][0]
