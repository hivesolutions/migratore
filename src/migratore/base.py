#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import sys

import legacy

ITER_SIZE = 10
""" The size to be used as reference for each iteration meaning
that each iteration of data retrieval will have this size """

ALIAS = dict(
    DB_HOST="HOST",
    DB_PORT="PORT",
    DB_UNIX_SOCKET="UNIX_SOCKET",
    DB_USER="USERNAME",
    DB_USERNAME="USERNAME",
    DB_PASSWORD="PASSWORD",
    DB_NAME="DB",
)
""" The map defining the various environment variable alias, mapping
the base value to the target value, this is required so that new
names are allowed to be used and legacy support is provided """

SEQUENCE_TYPES = (list, tuple)
""" The tuple defining the various data types that are considered
to be representing sequence structures under the python language """

VALID_TYPES = dict(
    HOST=str,
    PORT=int,
    UNIX_SOCKET=str,
    USERNAME=str,
    PASSWORD=str,
    DB=str,
    DB_URL=str,
    FS=str,
    DEBUG=int,
)
""" The dictionary defining the names and the expected data types
for the various environment variables accepted by the migratore
infra-structure as startup arguments """

TYPE_PRIORITY = dict(
    DB_HOST=10,
    HOST=1,
    DB_PORT=10,
    PORT=1,
    DB_UNIX_SOCKET=10,
    UNIX_SOCKET=1,
    DB_USER=10,
    DB_USERNAME=10,
    USERNAME=1,
    DB_PASSWORD=10,
    PASSWORD=1,
    DB_NAME=10,
    DB=1,
    FS=1,
    DEBUG=1,
)
""" The map/dictionary that defines the priority for each of the possible
value to be used for the configuration, this is critical to ensure
a proper usage of the environment variables (no error in overlap) """

SQL_TYPES_MAP = {
    "text": "text",
    "string": "varchar(255)",
    "integer": "integer",
    "long": "bigint",
    "float": "double precision",
    "decimal": "double precision",
    "date": "double precision",
    "data": "text",
    "metadata": "text",
}
""" The map containing the association of the entity types with
the corresponding sql types this values should always correspond
to the target values according to the orm specifics """

DEFAULT_CONFIG = dict(id_name="object_id", id_type="integer")
""" The map containing the default configuration to be used as the
fallback value for the creation of all the database object, this
will influence the way some operations will be done """


class Migratore(object):
    @classmethod
    def get_db(cls, *args, **kwargs):
        return cls.get_database()

    @classmethod
    def get_database(cls, *args, **kwargs):
        database = hasattr(cls, "_database") and cls._database
        if database:
            return database
        cls._env(args, kwargs)
        engine = kwargs.get("engine", "mysql")
        debug = kwargs.get("debug", False)
        method = getattr(cls, "_get_" + engine)
        database = method(*args, **kwargs)
        database.debug = debug
        database.open()
        cls._database = database
        return database

    @classmethod
    def get_test(cls, strict=False, echo=False, *args, **kwargs):
        database = cls.get_database(echo=echo, *args, **kwargs)
        is_test = database.name.endswith("test")
        is_migratore = database.name.endswith("migratore")
        if not is_test and not is_migratore:
            raise RuntimeError(
                "Test database '%s' is not test compliant" % database.name
            )
        table_count = database.count_tables()
        if strict and not table_count == 0:
            raise RuntimeError("Test Database '%s' is not empty" % database.name)
        return database

    @classmethod
    def get_fs(cls, *args, **kwargs):
        cls._env(args, kwargs)
        fs = kwargs.get("fs", "")
        fs = os.path.abspath(fs)
        fs = os.path.normpath(fs)
        return fs

    @classmethod
    def echo(cls, message, nl=True, file=sys.stdout):
        file.write(message)
        if nl:
            file.write("\n")

    @classmethod
    def echo_map(cls, map):
        largest = 0

        for key in legacy.iterkeys(map):
            key_l = len(key)
            if not key_l > largest:
                continue
            largest = key_l

        for key, value in legacy.iteritems(map):
            key_l = len(key)
            value_s = str(value)
            remaining = largest - key_l
            cls.echo(key, nl=False)
            for _index in legacy.xrange(remaining):
                cls.echo(" ", nl=False)
            cls.echo(" : ", nl=False)
            cls.echo(value_s)

    @classmethod
    def invalidate(cls):
        if not hasattr(cls, "_database"):
            return
        cls._database = None

    @classmethod
    def _get_mysql(cls, *args, **kwargs):
        from . import mysql

        try:
            import MySQLdb
        except ImportError:
            import pymysql

            MySQLdb = pymysql
        host = kwargs.get("host", "localhost")
        port = kwargs.get("port", 3306)
        unix_socket = kwargs.get("unix_socket", None)
        username = kwargs.get("username", "root")
        password = kwargs.get("password", "root")
        name = kwargs.get("db", "default")
        isolation = kwargs.get("isolation", "read committed")
        charset = kwargs.get("charset", "utf8")
        echo = kwargs.get("echo", True)
        password_l = len(password)
        display_l = min([password_l, 3])
        obfuscated = password[:display_l] + ((password_l - display_l) * "*")
        target = unix_socket if unix_socket else "%s:%d" % (host, port)
        if echo:
            cls.echo("mysql %s:%s@%s/%s" % (username, obfuscated, target, name))
        connection = (
            MySQLdb.connect(
                unix_socket=unix_socket, user=username, passwd=password, db=name
            )
            if unix_socket
            else MySQLdb.connect(
                host=host, port=port, user=username, passwd=password, db=name
            )
        )
        has_charset = hasattr(connection, "set_character_set")
        if has_charset:
            connection.set_character_set(charset)
        database = mysql.MySQLDatabase(cls, connection, name)
        database.execute("set session transaction isolation level %s" % isolation)
        return database

    @classmethod
    def _env(cls, args, kwargs):
        cls._environ_dot_env(args, kwargs)
        cls._environ(args, kwargs)
        cls._process(args, kwargs)

    @classmethod
    def _environ(cls, args, kwargs):
        environ = legacy.items(os.environ)
        sorter = lambda item: TYPE_PRIORITY.get(item[0], 0)
        environ.sort(key=sorter, reverse=True)
        for key, value in environ:
            key = ALIAS.get(key, key)
            key_l = key.lower()
            if key_l in kwargs:
                continue
            if not key in VALID_TYPES:
                continue
            _type = VALID_TYPES[key]
            kwargs[key_l] = _type(value)

    @classmethod
    def _environ_dot_env(cls, args, kwargs, name=".env", encoding="utf-8"):
        file_path = os.path.abspath(name)
        file_path = os.path.normpath(file_path)

        exists = os.path.exists(file_path)
        if not exists:
            return

        file = open(file_path, "rb")
        try:
            data = file.read()
        finally:
            file.close()
        if not data:
            return

        data = data.decode(encoding)
        data = data.strip()
        lines = data.splitlines()
        lines = [line.strip() for line in lines]

        envs = dict()

        for line in lines:
            line = line.strip()
            if not line:
                continue
            if line.startswith("#"):
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()
            if (
                value.startswith('"')
                and value.endswith('"')
                or value.startswith("'")
                and value.endswith("'")
            ):
                value = value[1:-1].replace('\\"', '"')
            envs[key] = value

        for key, value in legacy.iteritems(envs):
            key = ALIAS.get(key, key)
            key_l = key.lower()
            if key_l in kwargs:
                continue
            if not key in VALID_TYPES:
                continue
            _type = VALID_TYPES[key]
            kwargs[key_l] = _type(value)

    @classmethod
    def _process(cls, args, kwargs):
        if "db_url" in kwargs:
            cls._process_db_url(kwargs["db_url"], kwargs)

    @classmethod
    def _process_db_url(cls, url, kwargs, override=True):
        url_p = legacy.urlparse(url)
        if not "host" in kwargs or override:
            kwargs["host"] = str(url_p.hostname)
        if not "port" in kwargs or override:
            if url_p.port == None and "port" in kwargs:
                del kwargs["port"]
            elif not url_p.port == None:
                kwargs["port"] = int(url_p.port)
        if not "username" in kwargs or override:
            if url_p.username == None and "username" in kwargs:
                del kwargs["username"]
            elif not url_p.username == None:
                kwargs["username"] = str(url_p.username)
        if not "password" in kwargs or override:
            if url_p.password == None and "password" in kwargs:
                del kwargs["password"]
            elif not url_p.password == None:
                kwargs["password"] = str(url_p.password)
        if not "db" in kwargs or override:
            kwargs["db"] = str(url_p.path).strip("/")


class Console(object):
    def echo(self, *args, **kwargs):
        Migratore.echo(*args, **kwargs)

    def begin(self, message):
        message = self.title(message)
        self.echo("  * %s...\r" % message, False)

    def end(self, message):
        message = self.title(message)
        self.echo("  * %s... done     " % message)

    def percent(self, message, percentage):
        message = self.title(message)
        self.echo("  * %s [%d/100]...\r" % (message, percentage), False)

    def title(self, value):
        if not value:
            return value
        values = value.split(" ")
        values[0] = values[0].title()
        return " ".join(values)

    def is_tty(self):
        """
        Verifies if the current output/input methods are considered
        to be compliant with the typical console strategy (tty).

        This is important as it may condition the wat the console
        output will be made (carriage return, colors, etc).

        :rtype: bool
        :return: If the current standard output/input methods are
        compliant with tty standard.
        """

        if os.name == "nt":
            return self._is_tty_win()
        else:
            return self._is_tty_unix()

    def _is_tty_unix(self):
        return sys.stdin.isatty()

    def _is_tty_win(self):
        import msvcrt

        is_tty = sys.stdin.isatty()
        fileno = sys.stdin.fileno()
        mode_value = msvcrt.setmode(fileno, os.O_TEXT)  # @UndefinedVariable
        return is_tty and mode_value == 0x4000


class Database(Console):
    def __init__(
        self, owner=None, connection=None, name=None, debug=False, config=DEFAULT_CONFIG
    ):
        self.owner = owner
        self.connection = connection
        self.name = name
        self.debug = debug
        self.config = config
        self.engine = "undefined"
        self.types_map = dict(SQL_TYPES_MAP)
        self._apply_types()

    def execute(self, query, fetch=True, encoding="utf-8"):
        # ensures that the provided query string is encoded as
        # an unicode string, note that the encoding to be used
        # is the one provided for the next encoding operation
        is_unicode = type(query) == legacy.UNICODE
        if not is_unicode:
            query = query.decode(encoding)

        # debugs some information to the standard output this
        # may be useful for debugging purposes
        self._debug(query, title=self.engine)

        # in case the encoding parameter is defined encodes the
        # provided query string into a proper bytes string using
        # the provided encoding value for the encoding
        if encoding:
            query = query.encode(encoding)

        # creates a new cursor using the current connection
        # this cursor is going to be used for the execution
        cursor = self.connection.cursor()

        try:
            # executes the query using the current cursor
            # then closes the cursor avoid the leak of
            # cursor objects (memory reference leaking)
            cursor.execute(query)

            # in case the (auto) fetch flag is set not the cursor
            # should be closed right after the query in order
            # to avoid any memory leak in execution
            if not fetch:
                return None

            # fetches the complete set of results from the cursor
            # and returns these results to the caller method as this
            # is the expected behavior for the current execution
            result = cursor.fetchall()
        finally:
            # in case there's an issue whatsoever the cursor should
            # be closed in order to avoid possible cursor leak
            cursor.close()

        # returns the final result value to the caller method
        # according to the cursor execution
        return result

    def open(self):
        self.ensure_system()

    def close(self):
        self.connection.commit()

    def rollback(self):
        self.connection.rollback()

    def commit(self):
        self.connection.commit()

    def create(self):
        buffer = self._buffer()
        buffer.write("create database ")
        buffer.write(self.name)
        buffer.execute()
        self.owner.invalidate()

    def drop(self):
        buffer = self._buffer()
        buffer.write("drop database ")
        buffer.write(self.name)
        buffer.execute()
        self.owner.invalidate()

    def clear(self):
        self.drop()
        self.create()

    def table(self, *args, **kwargs):
        return Table(*args, **kwargs)

    def timestamp(self):
        table = self.get_table("migratore")
        timestamp = table.get(
            "timestamp", order_by=(("timestamp", "desc"),), result="success"
        )
        return timestamp

    def ensure_system(self):
        exists = self.exists_table("migratore")
        if not exists:
            self.create_system()
        self.ensure_system_c()

    def ensure_system_c(self):
        table = self.get_table("migratore")
        table.ensure_column("uuid", type="string", index=True)
        table.ensure_column("timestamp", type="integer", index=True)
        table.ensure_column("name", type="string", index=True)
        table.ensure_column("description", type="text")
        table.ensure_column("result", type="string", index=True)
        table.ensure_column("error", type="text")
        table.ensure_column("traceback", type="text")
        table.ensure_column("operator", type="text")
        table.ensure_column("operation", type="text")
        table.ensure_column("start", type="integer", index=True)
        table.ensure_column("end", type="integer", index=True)
        table.ensure_column("duration", type="integer", index=True)
        table.ensure_column("start_s", type="string")
        table.ensure_column("end_s", type="string")

    def create_system(self):
        self.create_table("migratore")
        self.ensure_system_c()

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
        buffer.write(" ")
        buffer.write(" primary key ")
        buffer.write(")")
        buffer.execute()
        table = self.table(self, name, id_name)
        table.index_column(id_name)
        return table

    def drop_table(self, name):
        buffer = self._buffer()
        buffer.write("drop table ")
        buffer.write(name)
        buffer.execute()

    def get_table(self, name):
        id_name = self.config["id_name"]
        self.assert_table(name)
        return self.table(self, name, id_name)

    def assert_table(self, name):
        exists = self.exists_table(name)
        if not exists:
            raise RuntimeError("Table '%s' does not exist" % name)

    def exists_table(self, name):
        raise RuntimeError("Not implemented")

    def names_table(self, name):
        raise RuntimeError("Not implemented")

    def create_relation(self, name, *fields):
        id_type = self.config["id_type"]
        buffer = self._buffer()
        buffer.write("create table ")
        buffer.write(name)
        buffer.write("(")
        is_first = True
        for field in fields:
            if is_first:
                is_first = False
            else:
                buffer.write(", ")
            buffer.write(field)
            buffer.write(" ")
            buffer.write_type(id_type)
        buffer.write(", ")
        buffer.write("constraint %s_pk primary key(" % name)
        is_first = True
        for field in fields:
            if is_first:
                is_first = False
            else:
                buffer.write(", ")
            buffer.write(field)
        buffer.write(")")
        buffer.write(")")
        buffer.execute()
        table = self.table(self, name)
        for field in fields:
            table.index_column(field, types=("hash",))
        return table

    def _debug(self, message, title=None):
        if not self.debug:
            return
        message = self._format(message, title)
        sys.stderr.write(message + "\n")

    def _format(self, message, title):
        if title:
            message = "[%s] %s" % (title, message)
        return message

    def _apply_types(self):
        pass

    def _buffer(self):
        buffer = legacy.StringIO()
        _write = buffer.write

        def write(value):
            is_bytes = type(value) == legacy.BYTES
            if is_bytes:
                value = value.decode("utf-8")
            _write(value)

        def write_type(type):
            type_s = self._type(type)
            buffer.write(type_s)

        def write_value(value):
            value_s = self._escape(value)
            buffer.write(value_s)

        def join():
            value = buffer.getvalue()
            is_unicode = isinstance(value, legacy.UNICODE)
            if is_unicode:
                return value
            return value.decode("utf-8")

        def execute(fetch=False):
            query = buffer.join()
            return self.execute(query, fetch=fetch)

        buffer.write = write
        buffer.write_type = write_type
        buffer.write_value = write_value
        buffer.join = join
        buffer.execute = execute
        return buffer

    def _type(self, type):
        return self.types_map[type]

    def _escape(self, value):
        value_t = type(value)

        if value_t == type(None):
            return "null"
        if not value_t in legacy.STRINGS:
            return str(value)

        value = value.replace("'", "''")
        value = value.replace("\\", "\\\\")
        value = value.replace('"', '""')

        return "'" + value + "'"


class Table(Console):
    def __init__(self, owner, name, identifier=None):
        self.owner = owner
        self.name = name
        self.identifier = identifier

    def insert(self, **kwargs):
        self._identifier(kwargs)
        into = self._into(kwargs)
        buffer = self.owner._buffer()
        buffer.write("insert into ")
        buffer.write(self.name)
        buffer.write(" ")
        buffer.write(into)
        buffer.execute()

    def select(self, fnames=None, where=None, range=None, order_by=None, **kwargs):
        fnames = fnames or self.owner.names_table(self.name)
        names = self._names(fnames)
        buffer = self.owner._buffer()
        buffer.write("select ")
        buffer.write(names)
        buffer.write(" from ")
        buffer.write(self.name)
        self.tail(buffer, where=where, range=range, order_by=order_by, **kwargs)
        results = buffer.execute(fetch=True)
        results = self._pack(fnames, results)
        return results

    def update(self, fvalues, where=None, **kwargs):
        values = self._values(fvalues)
        buffer = self.owner._buffer()
        buffer.write("update ")
        buffer.write(self.name)
        buffer.write(" set ")
        buffer.write(values)
        self.tail(buffer, where=where, **kwargs)
        buffer.execute()

    def delete(self, where=None, **kwargs):
        buffer = self.owner._buffer()
        buffer.write("delete from ")
        buffer.write(self.name)
        self.tail(buffer, where, **kwargs)
        buffer.execute()

    def count(self, where=None, range=None, **kwargs):
        buffer = self.owner._buffer()
        buffer.write("select count(1) from ")
        buffer.write(self.name)
        self.tail(buffer, where=where, range=range, **kwargs)
        results = buffer.execute(fetch=True)
        count = results[0][0]
        return count

    def drop(self):
        buffer = self.owner._buffer()
        buffer.write("drop table ")
        buffer.write(self.name)
        buffer.execute()

    def get(self, *args, **kwargs):
        result = self.select(*args, **kwargs)
        if not result:
            return None
        return result[0]

    def first(self, *args, **kwargs):
        kwargs["order_by"] = ((self.identifier, "asc"),)
        value = self.get(*args, **kwargs)
        return value

    def last(self, *args, **kwargs):
        kwargs["order_by"] = ((self.identifier, "desc"),)
        value = self.get(*args, **kwargs)
        return value

    def clear(self):
        return self.delete()

    def tail(self, buffer, where=None, range=None, order_by=None, **kwargs):
        where = where or self._where(kwargs)
        if where:
            buffer.write(" where ")
            buffer.write(where)
        if range:
            offset = str(range[0])
            limit = str(range[1])
            buffer.write(" limit ")
            buffer.write(limit)
            buffer.write(" offset ")
            buffer.write(offset)
        if order_by:
            is_first = True
            buffer.write(" order by ")
            for order in order_by:
                if is_first:
                    is_first = False
                else:
                    buffer.write(", ")
                order_s = " ".join(order)
                buffer.write(order_s)

    def ensure_column(self, name, type="integer", index=False, types=("hash", "btree")):
        names = self.owner.names_table(self.name)
        if name in names:
            return
        self.add_column(name, type=type, index=index, types=types)

    def add_column(self, name, type="integer", index=False, types=("hash", "btree")):
        buffer = self.owner._buffer()
        buffer.write("alter table ")
        buffer.write(self.name)
        buffer.write(" add column ")
        buffer.write(name)
        buffer.write(" ")
        buffer.write_type(type)
        buffer.execute()
        if index:
            self.index_column(name, types=types)

    def add_foreign(self, name, type="integer", index=True, types=("hash",)):
        self.add_column(name, type=type, index=index, types=types)

    def remove_column(self, name):
        buffer = self.owner._buffer()
        buffer.write("alter table ")
        buffer.write(self.name)
        buffer.write(" drop column ")
        buffer.write(name)
        buffer.execute()

    def change_column(self, name, new_name=None, type=None):
        if not new_name:
            new_name = name
        buffer = self.owner._buffer()
        buffer.write("alter table ")
        buffer.write(self.name)
        buffer.write(" change ")
        buffer.write(name)
        buffer.write(" ")
        buffer.write(new_name)
        if type:
            buffer.write(" ")
            buffer.write_type(type)
        buffer.execute()

    def index_column(self, name, types=("hash", "btree")):
        for type in types:
            self.create_index(name, type=type)

    def create_index(self, name, type="hash"):
        pass

    def drop_index(self, name):
        pass

    def run(self, callable, count, title=None):
        index = 0

        while True:
            if index >= count:
                break

            callable(self, index)

            if not title:
                continue

            ratio = float(index) / float(count)
            pecentage = int(ratio * 100)

            self.percent(title, pecentage)

            index += 1

        if not title:
            return

        self.end("%s" % title)

    def apply(
        self, callable, title=None, limit=None, eager=False, where=None, **kwargs
    ):
        count = self.count(where=where, **kwargs)
        if not limit == None:
            count = limit if count > limit else count

        index = 0
        if eager:
            source = self.select(where=where, **kwargs)

        while True:
            if index >= count:
                break
            range = (index, ITER_SIZE)
            results = (
                source[index : index + ITER_SIZE]
                if eager
                else self.select(where=where, range=range, **kwargs)
            )
            for result in results:
                callable(result)
            index += ITER_SIZE

            if not title:
                continue

            ratio = float(index) / float(count)
            pecentage = int(ratio * 100)

            self.percent(title, pecentage)

        if not title:
            return

        self.end("%s" % title)

    def echo(self, *args, **kwargs):
        self.owner.echo(*args, **kwargs)

    def _pack(self, names, values):
        names_t = type(names)
        multiple = names_t in SEQUENCE_TYPES

        result = []

        for value in values:
            _zip = zip(names, value)
            value_m = Result(self, _zip) if multiple else value[0]
            result.append(value_m)

        return tuple(result)

    def _names(self, args):
        args_t = type(args)
        if not args_t in SEQUENCE_TYPES:
            return args
        return ", ".join(args)

    def _values(self, kwargs):
        buffer = self.owner._buffer()

        is_first = True

        for key, value in legacy.iteritems(kwargs):
            if is_first:
                is_first = False
            else:
                buffer.write(", ")
            buffer.write(key)
            buffer.write(" = ")
            buffer.write_value(value)

        return buffer.join()

    def _into(self, kwargs):
        buffer = self.owner._buffer()

        is_first = True

        names = legacy.keys(kwargs)
        names_s = ", ".join(names)

        buffer.write("(")
        buffer.write(names_s)
        buffer.write(") values(")

        for value in legacy.values(kwargs):
            if is_first:
                is_first = False
            else:
                buffer.write(", ")
            buffer.write_value(value)

        buffer.write(")")

        return buffer.join()

    def _where(self, kwargs):
        buffer = self.owner._buffer()

        is_first = True

        for key, value in legacy.iteritems(kwargs):
            if is_first:
                is_first = False
            else:
                buffer.write(" and ")
            buffer.write(key)
            buffer.write(" = ")
            buffer.write_value(value)

        return buffer.join()

    def _identifier(self, kwargs):
        if self.identifier in kwargs:
            return
        value = (self.last(self.identifier) or 0) + 1
        kwargs[self.identifier] = value


class Result(dict):
    def __init__(self, owner, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.owner = owner
        self.identifier = owner.identifier

    def update(self, **kwargs):
        value = self[self.identifier]
        _kwargs = {self.identifier: value}
        self.owner.update(kwargs, **_kwargs)

    def join(self, table_name):
        value = self[self.identifier]
        db = self.owner.owner
        table = db.get_table(table_name)
        kwargs = {self.identifier: value}
        return table.get(**kwargs)
