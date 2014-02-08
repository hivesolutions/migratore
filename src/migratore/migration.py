#!/usr/bin/python
# -*- coding: utf-8 -*-

import time
import datetime
import traceback

import base

class Migration(object):

    def __init__(self):
        self.uuid = None
        self.timestamp = None
        self.name = None
        self.description = None

    def start(self, operator = "Administrator"):
        db = base.Migratore.get_db()
        try: self._start(db, operator)
        finally: db.close()

    def _start(self, db, operator):
        result = "success"
        error = None
        lines = None
        start = time.time()

        try: self.run(db)
        except BaseException, exception:
            db.rollback()
            lines = traceback.format_exc().splitlines()
            lines = "\n".join(lines)
            result = "error"
            error = str(exception)
        else: db.commit()

        end = time.time()
        start = int(start)
        end = int(end)
        duration = end - start

        start_s = self._time_s(start)
        end_s = self._time_s(end)

        table = db.get_table("migratore")
        table.insert(
            uuid = self.uuid,
            timestamp = self.timestamp,
            name = self.name,
            description = self.description,
            result = result,
            error = error,
            traceback = lines,
            operator = operator,
            start = start,
            end = end,
            duration = duration,
            start_s = start_s,
            end_s = end_s,
        )
        db.commit()

    def run(self, db):
        raise RuntimeError("Not implemented")

    def _time_s(self, timestamp):
        date_time = datetime.datetime.utcfromtimestamp(timestamp)
        return date_time.strftime("%d %b %Y %H:%M:%S")
