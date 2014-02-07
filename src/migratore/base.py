#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import types
import StringIO

SEQUENCE_TYPES = (
    types.ListType,
    types.TupleType
)
""" The tuple defining the various data types that are considered
to be representing sequences under the python language """

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
    def get_db(cls, *args, **kwargs):
        return cls.get_database()

    @classmethod
    def get_database(cls, *args, **kwargs):
        cls._environ(args, kwargs)
        engine = kwargs.get("engine", "mysql")
        method = getattr(cls, "_get_" + engine)
        database = method(*args, **kwargs)
        database.open()
        return database

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

class Database(object):

    def __init__(self, connection, name, config = DEFAULT_CONFIG):
        self.connection = connection
        self.name = name
        self.config = config
        self.engine = "undefined"
        self.types_map = dict(SQL_TYPES_MAP)
        self._apply_types()

    def execute(self, query, fetch = True):
        # debugs some information to the standard output this
        # may be useful for debugging purposes
        self._debug(query, title = self.engine)

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

    def open(self):
        pass

    def close(self):
        self.connection.commit()

    def rollback (self):
        self.connection.rollback ()

    def commit(self):
        self.connection.commit()

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
        self.ensure_table(name)
        return Table(self, name)

    def ensure_table(self, name):
        exists = self.exists_table(name)
        if not exists: raise RuntimeError("Table '%s' does not exist" % name)

    def exists_table(self, name):
        raise RuntimeError("Not implemented")

    def _debug(self, message, title = None):
        is_debug = self.config.get("debug", True)
        if not is_debug: return
        if title: print "[%s] %s" % (title, message)
        else: print message

    def _apply_types(self):
        pass

    def _buffer(self):
        buffer = StringIO.StringIO()

        def write_type(type):
            type_s = self._type(type)
            buffer.write(type_s)

        def write_value(value):
            value_s = self._escape(value)
            buffer.write(value_s)

        def join():
            return buffer.getvalue()

        def execute(fetch = False):
            query = buffer.join()
            return self.execute(query, fetch = fetch)

        buffer.write_type = write_type
        buffer.write_value = write_value
        buffer.join = join
        buffer.execute = execute
        return buffer

    def _type(self, type):
        return self.types_map[type]

    def _escape(self, value):
        value_t = type(value)

        if not value_t in types.StringTypes: return str(value)

        if value_t == types.UnicodeType: value.encode("utf-8")

        value = value.replace("'", "''")
        value = value.replace("\\", "\\\\")
        value = value.replace("\"", "\"\"")

        return "'" + value + "'"

class MysqlDatabase(Database):

    # @todo se tiver bulk operations por agulam informacao de progresso
    # e por isso com o \n

    def __init__(self, *args, **kwargs):
        Database.__init__(self, *args, **kwargs)
        self.engine = "mysql"
        self.isolation_level = "read committed"

    def open(self):
        Database.open(self)
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
        Database._apply_types(self)
        self.types_map["text"] = "longtext"
        self.types_map["data"] = "longtext"
        self.types_map["metadata"] = "longtext"

class Table(object):

    def __init__(self, owner, name):
        self.owner = owner
        self.name = name

    def insert(self, **kwargs):
        into = self._into(kwargs)
        buffer = self.owner._buffer()
        buffer.write("insert into ")
        buffer.write(self.name)
        buffer.write(" ")
        buffer.write(into)
        buffer.execute()

    def select(self, fnames, where = None, **kwargs):
        names = self._names(fnames)
        where = where or self._where(kwargs)
        buffer = self.owner._buffer()
        buffer.write("select ")
        buffer.write(names)
        buffer.write(" from ")
        buffer.write(self.name)
        if where:
            buffer.write(" where ")
            buffer.write(where)
        results = buffer.execute(fetch = True)
        results = self._pack(fnames, results)
        return results

    def update(self, fvalues, where = None, **kwargs):
        values = self._values(fvalues)
        where = where or self._where(kwargs)
        buffer = self.owner._buffer()
        buffer.write("update ")
        buffer.write(self.name)
        buffer.write(" set ")
        buffer.write(values)
        if where:
            buffer.write(" where ")
            buffer.write(where)
        buffer.execute()

    def delete(self, where = None, **kwargs):
        where = where or self._where(kwargs)
        buffer = self.owner._buffer()
        buffer.write("delete from ")
        buffer.write(self.name)
        if where:
            buffer.write(" where ")
            buffer.write(where)
        buffer.execute()

    def count(self, where = None, **kwargs):
        where = where or self._where(kwargs)
        buffer = self.owner._buffer()
        buffer.write("select count(1) from ")
        buffer.write(self.name)
        if where:
            buffer.write(" where ")
            buffer.write(where)
        results = buffer.execute(fetch = True)
        count = results[0][0]
        return count

    def drop(self):
        buffer = self.owner._buffer()
        buffer.write("drop table ")
        buffer.write(self.name)
        buffer.execute()

    def get(self, *args, **kwargs):
        return self.select(*args, **kwargs)[0]

    def clear(self):
        return self.delete()

    def add_column(self, name, type = "integer"):
        buffer = self.owner._buffer()
        buffer.write("alter table ")
        buffer.write(self.name)
        buffer.write(" add column ")
        buffer.write(name)
        buffer.write(" ")
        buffer.write_type(type)
        buffer.execute()

    def _pack(self, names, values):
        names_t = type(names)
        multiple = names_t in SEQUENCE_TYPES

        result = []

        for value in values:
            value_m = dict(zip(names, value)) if multiple else value[0]
            result.append(value_m)

        return tuple(result)

    def _names(self, args):
        args_t = type(args)
        if not args_t in SEQUENCE_TYPES: return args
        return ", ".join(args)

    def _values(self, kwargs):
        buffer = self.owner._buffer()

        is_first = True

        for key, value in kwargs.iteritems():
            if is_first: is_first = False
            else: buffer.write(", ")
            buffer.write(key)
            buffer.write(" = ")
            buffer.write_value(value)

        return buffer.join()

    def _into(self, kwargs):
        buffer = self.owner._buffer()

        is_first = True

        names = kwargs.keys()
        names_s = ", ".join(names)

        buffer.write("(")
        buffer.write(names_s)
        buffer.write(") values(")

        for value in kwargs.values():
            if is_first: is_first = False
            else: buffer.write(", ")
            buffer.write_value(value)

        buffer.write(')')

        return buffer.join()

    def _where(self, kwargs):
        buffer = self.owner._buffer()

        is_first = True

        for key, value in kwargs.iteritems():
            if is_first: is_first = False
            else: buffer.write(" and ")
            buffer.write(key)
            buffer.write(" = ")
            buffer.write_value(value)

        return buffer.join()

    def _escape(self, value):
        return self.owner._
