#!/usr/bin/python
# -*- coding: utf-8 -*-

import os
import uuid
import time
import datetime
import traceback

import base
import loader

class Migration(base.Console):

    def __init__(self):
        self.uuid = None
        self.timestamp = None
        self.description = None

    def __cmp__(self, value):
        return cmp(self.timestamp, value.timestamp)

    @classmethod
    def list(cls):
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            executions = table.select(
                order_by = (("object_id", "asc"),),
                result = "success"
            )

            is_first = True
            for execution in executions:
                if is_first: is_first = False
                else: base.Migratore.echo("")
                cls._execution(execution, is_first = is_first)

        finally: db.close()

    @classmethod
    def errors(cls):
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            executions = table.select(
                order_by = (("object_id", "asc"),),
                result = "error"
            )

            is_first = True
            for execution in executions:
                if is_first: is_first = False
                else: base.Migratore.echo("")
                cls._execution(execution, is_first = is_first)
                cls._error(execution, is_first = is_first)

        finally: db.close()

    @classmethod
    def trace(cls, id):
        object_id = int(id)
        db = base.Migratore.get_db()
        try:
            table = db.get_table("migratore")
            execution = table.get(object_id = object_id)
            traceback = execution["traceback"]
            base.Migratore.echo(traceback)
        finally: db.close()

    @classmethod
    def upgrade(self, path = None):
        path = path or "."
        path = os.path.abspath(path)
        _loader = loader.DirectoryLoader(path)
        _loader.upgrade()

    @classmethod
    def generate(cls, path = None):
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
        try: file.write(data)
        finally: file.close()
        base.Migratore.echo("Migration file '%s' generated" % path)

    @classmethod
    def template(cls, path, *args):
        file = open(path, "rb")
        try: contents = file.read()
        finally: file.close()

        return contents % args

    @classmethod
    def _time_s(cls, timestamp):
        date_time = datetime.datetime.utcfromtimestamp(timestamp)
        return date_time.strftime("%d %b %Y %H:%M:%S")

    @classmethod
    def _execution(cls, execution, is_first = True):
        object_id = execution["object_id"]
        _uuid = execution["uuid"]
        timestamp = execution["timestamp"]
        description = execution["description"]
        operator = execution["operator"]
        duration = execution["duration"]
        start_s = execution["start_s"]
        end_s = execution["end_s"]
        timstamp_s = cls._time_s(timestamp)

        duration_l = "second" if duration == 1 else "seconds"

        base.Migratore.echo("ID          -  %s" % object_id)
        base.Migratore.echo("UUID        -  %s" % _uuid)
        base.Migratore.echo("Timestamp   -  %d (%s)" % (timestamp, timstamp_s))
        base.Migratore.echo("Description -  %s" % description)
        base.Migratore.echo("Operator    -  %s" % operator)
        base.Migratore.echo("Duration    -  %d %s" % (duration, duration_l))
        base.Migratore.echo("Start time  -  %s" % start_s)
        base.Migratore.echo("End time    -  %s" % end_s)

    @classmethod
    def _error(cls, execution, is_first = True):
        error = execution["error"]

        base.Migratore.echo("Error       -  %s" % error)

    def start(self, operator = "Administrator"):
        db = base.Migratore.get_db()
        try: return self._start(db, operator)
        finally: db.close()

    def run(self, db):
        self.echo("Running migration '%s'" % self.uuid)

    def cleanup(self, db):
        self.echo("Cleaning up...")

    def _start(self, db, operator):
        cls = self.__class__

        result = "success"
        error = None
        lines_s = None
        start = time.time()

        try: self.run(db)
        except BaseException, exception:
            db.rollback()
            lines = traceback.format_exc().splitlines()
            lines_s = "\n".join(lines)
            result = "error"
            error = str(exception)
            for line in lines: self.echo(line)
        else: db.commit()
        finally: self.cleanup(db)

        end = time.time()
        start = int(start)
        end = int(end)
        duration = end - start

        start_s = cls._time_s(start)
        end_s = cls._time_s(end)

        table = db.get_table("migratore")
        table.insert(
            uuid = self.uuid,
            timestamp = self.timestamp,
            description = self.description,
            result = result,
            error = error,
            traceback = lines_s,
            operator = operator,
            start = start,
            end = end,
            duration = duration,
            start_s = start_s,
            end_s = end_s,
        )
        db.commit()

        return result
