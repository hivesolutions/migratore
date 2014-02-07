#!/usr/bin/python
# -*- coding: utf-8 -*-

import base

class MysqlDatabase(base.Database):

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

    def exists_table(self, name):
        buffer = self._buffer()
        buffer.write("select count(*) ")
        buffer.write("from information_schema.tables where table_schema = '")
        buffer.write(self.name)
        buffer.write("' and table_name = '")
        buffer.write(name)
        buffer.write("'")
        counts = buffer.execute(fetch = True)
        exists = True if counts and counts[0][0] > 0 else False
        return exists

    def _apply_types(self):
        base.Database._apply_types(self)
        self.types_map["text"] = "longtext"
        self.types_map["data"] = "longtext"
        self.types_map["metadata"] = "longtext"
