#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import uuid
import time
import datetime
import traceback

from . import base
from . import loader


class Migration(base.Console):
    def __init__(self, uuid=None, timestamp=None, description=None):
        self.uuid = uuid
        self.timestamp = timestamp
        self.description = description

    def __cmp__(self, value):
        return self.timestamp.__cmp__(value.timestamp)

    def __lt__(self, value):
        return self.timestamp < value.timestamp

    def __gt__(self, value):
        return self.timestamp > value.timestamp

    def __eq__(self, value):
        return self.timestamp == value.timestamp

    def __le__(self, value):
        return self.timestamp <= value.timestamp

    def __ge__(self, value):
        return self.timestamp >= value.timestamp

    def __ne__(self, value):
        return self.timestamp != value.timestamp

    @classmethod
    def environ(cls):
        args = list()
        kwargs = dict()
        base.Migratore._environ(args, kwargs)
        base.Migratore.echo_map(kwargs)

    @classmethod
    def list(cls):
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            executions = table.select(
                order_by=(("object_id", "asc"),), result="success"
            )

            is_first = True
            for execution in executions:
                if is_first:
                    is_first = False
                else:
                    base.Migratore.echo("")
                cls._execution(execution, is_first=is_first)

        finally:
            db.close()

    @classmethod
    def errors(cls):
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            executions = table.select(order_by=(("object_id", "asc"),), result="error")

            is_first = True
            for execution in executions:
                if is_first:
                    is_first = False
                else:
                    base.Migratore.echo("")
                cls._execution(execution, is_first=is_first)
                cls._error(execution, is_first=is_first)

        finally:
            db.close()

    @classmethod
    def mark(self, *args, **kwargs):
        db = base.Migratore.get_db(*args, **kwargs)
        timestamp = db.timestamp()
        timestamp = timestamp or 0
        migration = MarkMigration()
        migration.start()

    @classmethod
    def trace(cls, id):
        object_id = int(id)
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            execution = table.get(object_id=object_id)
            traceback = execution["traceback"]
            base.Migratore.echo(traceback)
        finally:
            db.close()

    @classmethod
    def rebuild(self, id, *args, **kwargs):
        path = "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.rebuild(id, *args, **kwargs)

    @classmethod
    def upgrade(self, path=None, *args, **kwargs):
        path = path or "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.upgrade(*args, **kwargs)

    @classmethod
    def generate(cls, path=None):
        _uuid = uuid.uuid4()
        _uuid = str(_uuid)
        timestamp = time.time()
        timestamp = int(timestamp)
        description = "migration %s" % _uuid
        args = (_uuid, timestamp, description)
        path = path or str(timestamp) + ".py"

        file_path = os.path.abspath(__file__)
        dir_path = os.path.dirname(file_path)
        templates_path = os.path.join(dir_path, "templates")
        template_path = os.path.join(templates_path, "migration.py.tpl")

        base.Migratore.echo("Generating migration '%s'..." % _uuid)
        data = cls.template(template_path, *args)
        file = open(path, "wb")
        try:
            file.write(data)
        finally:
            file.close()
        base.Migratore.echo("Migration file '%s' generated" % path)

    @classmethod
    def template(cls, path, *args, **kwargs):
        encoding = kwargs.get("encoding", "utf-8")

        file = open(path, "rb")
        try:
            contents = file.read()
        finally:
            file.close()

        contents = contents.decode(encoding)
        result = contents % args
        return result.encode(encoding)

    @classmethod
    def _time_s(cls, timestamp):
        date_time = datetime.datetime.utcfromtimestamp(timestamp)
        return date_time.strftime("%d %b %Y %H:%M:%S")

    @classmethod
    def _execution(cls, execution, is_first=True):
        object_id = execution["object_id"]
        _uuid = execution["uuid"]
        timestamp = execution["timestamp"]
        description = execution["description"]
        operation = execution["operation"]
        operator = execution["operator"]
        duration = execution["duration"]
        start_s = execution["start_s"]
        end_s = execution["end_s"]
        timstamp_s = cls._time_s(timestamp)

        duration_l = "second" if duration == 1 else "seconds"

        base.Migratore.echo("ID          : %s" % object_id)
        base.Migratore.echo("UUID        : %s" % _uuid)
        base.Migratore.echo("Timestamp   : %d (%s)" % (timestamp, timstamp_s))
        base.Migratore.echo("Description : %s" % description)
        base.Migratore.echo("Operation   : %s" % operation)
        base.Migratore.echo("Operator    : %s" % operator)
        base.Migratore.echo("Duration    : %d %s" % (duration, duration_l))
        base.Migratore.echo("Start time  : %s" % start_s)
        base.Migratore.echo("End time    : %s" % end_s)

    @classmethod
    def _error(cls, execution, is_first=True):
        error = execution["error"]

        base.Migratore.echo("Error       :  %s" % error)

    def start(self, operation="run", operator="Administrator"):
        db = base.Migratore.get_db()
        try:
            return self._start(db, operation, operator)
        finally:
            db.close()

    def run(self, db):
        self.echo("Running migration '%s'" % self.uuid)
        if self.description:
            self.echo("%s" % self.description)

    def partial(self, db):
        self.echo("Running partial '%s'" % self.uuid)
        if self.description:
            self.echo("%s" % self.description)

    def cleanup(self, db):
        self.echo("Cleaning up...")

    def _start(self, db, operation, operator):
        cls = self.__class__

        result = "success"
        error = None
        lines_s = None
        start = time.time()

        method = getattr(self, operation)
        try:
            method(db)
        except Exception as exception:
            db.rollback()
            lines = traceback.format_exc().splitlines()
            lines_s = "\n".join(lines)
            result = "error"
            error = str(exception)
            for line in lines:
                self.echo(line)
        else:
            db.commit()
        finally:
            self.cleanup(db)

        operation_s = operation.title()

        end = time.time()
        start = int(start)
        end = int(end)
        duration = end - start

        start_s = cls._time_s(start)
        end_s = cls._time_s(end)

        table = db.get_table("migratore")
        table.insert(
            uuid=self.uuid,
            timestamp=self.timestamp,
            description=self.description,
            result=result,
            error=error,
            traceback=lines_s,
            operation=operation_s,
            operator=operator,
            start=start,
            end=end,
            duration=duration,
            start_s=start_s,
            end_s=end_s,
        )
        db.commit()

        return result


class MarkMigration(Migration):
    def __init__(self):
        Migration.__init__(self)
        self.uuid = "da023aab-736d-40a6-8e9b-c6175c1241f5"
        self.timestamp = int(time.time())
        self.description = "marks the initial stage of the data source"

    def start(self, *args, **kwargs):
        db = base.Migratore.get_db()
        table = db.get_table("migratore")
        count = table.count(result="success")
        if count > 0:
            return
        return Migration.start(self, *args, **kwargs)
