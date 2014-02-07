#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import StringIO

VALID_TYPES = dict(
    HOST = str,
    PORT = int,
    USERNAME = str,
    PASSWORD = str,
    DB = str
)
""" The dictionary defining the names and the expected data types
for the various environment variables accepted by the migratore
infra-structure as startup arguments """

SQL_TYPES_MAP = {
    "text" : "text",
    "string" : "varchar(255)",
    "integer" : "integer",
    "long" : "bigint",
    "float" : "double precision",
    "date" : "double precision",
    "data" : "text",
    "metadata" : "text"
}
""" The map containing the association of the entity types with
the corresponding sql types this values should always correspond
to the target values according to the orm specifics """

DEFAULT_CONFIG = dict(
    id_name = "object_id",
    id_type = "integer"
)
""" The map containing the default configuration to be used as the
fallback value for the creation of all the database object, this
will influence the way some operations will be done """

class Migratore(object):

    @classmethod
    def get_database(cls, *args, **kwargs):
        cls._environ(args, kwargs)
        engine = kwargs.get("engine", "mysql")
        method = getattr(cls, "_get_" + engine)
        return method(*args, **kwargs)

    @classmethod
    def _get_mysql(cls, *args, **kwargs):
        import MySQLdb
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 3306)
        username = kwargs.get("username", "root")
        password = kwargs.get("password", "root")
        name = kwargs.get("db", "default")
        connection = MySQLdb.connect(
            host,
            port = port,
            user = username,
            passwd = password,
            db = name
        )
        return MysqlDatabase(connection, name)

    @classmethod
    def _environ(cls, args, kwargs):
        for key, value in os.environ.iteritems():
            if not key in VALID_TYPES: continue
            _type = VALID_TYPES[key]
            key_l = key.lower()
            kwargs[key_l] = _type(value)

class Connection(object):

    def __init__(self, conn, name):
        self.conn = conn
        self.name = name

class Database(object):

    def __init__(self, connection, name, config = DEFAULT_CONFIG):
        self.connection = connection
        self.name = name
        self.config = config
        self.types_map = dict(SQL_TYPES_MAP)
        self._apply_types()

    def execute(self, query, fetch = True):
        # creates a new cursor using the current connection
        # this cursor is going to be used for the execution
        cursor = self.connection.cursor()

        # executes the query using the current cursor
        # then closes the cursor avoid the leak of
        # cursor objects (memory reference leaking)
        try: cursor.execute(query)
        except: cursor.close(); raise

        # in case the (auto) fetch flag is set not the cursor
        # should be closed right after the query in order
        # to avoid any memory leak in execution
        if not fetch: cursor.close(); return

        # fetches the complete set of results from the cursor
        # and returns these results to the caller method as this
        # is the expected behavior for the current execution
        try: result = cursor.fetchall()
        finally: cursor.close()
        return result

    def create_table(self, name):
        id_name = self.config["id_name"]
        id_type = self.config["id_type"]
        buffer = self._buffer()
        buffer.write("create table ")
        buffer.write(name)
        buffer.write("(")
        buffer.write(id_name)
        buffer.write(" ")
        buffer.write_type(id_type)
        buffer.write(")")
        buffer.execute()
        return Table(self, name)

    def get_table(self, name):
        self.exists_table(name)
        return Table(self, name)

    def exists_table(self, name):
        raise RuntimeError("Not implemented")

    def _apply_types(self):
        pass

    def _buffer(self):
        buffer = StringIO.StringIO()

        def write_type(type):
            type_s = self._type(type)
            buffer.write(type_s)

        def join():
            return buffer.getvalue()

        def execute(fetch = False):
            query = buffer.join()
            return self.execute(query, fetch = fetch)

        buffer.write_type = write_type
        buffer.join = join
        buffer.execute = execute
        return buffer

    def _type(self, type):
        return self.types_map[type]

class MysqlDatabase(Database):

    # @todo se tiver bulk operations por agulam informacao de progresso
    # e por isso com o \n



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
        Database._apply_types(self)
        self.types_map["text"] = "longtext"
        self.types_map["data"] = "longtext"
        self.types_map["metadata"] = "longtext"

class Table(object):

    def __init__(self, owner, name):
        self.owner = owner
        self.name = name

    def add_column(self, name, type = "integer"):
        buffer = self.owner._buffer()
        buffer.write("alter table ")
        buffer.write(self.name)
        buffer.write(" add column ")
        buffer.write(name)
        buffer.write(" ")
        buffer.write_type(type)
        buffer.execute()

if __name__ == "__main__":
    database = Migratore.get_database()
    table = database.create_table("users")
    #table = database.get_table("users")
    table.add_column("username", type = "text")
