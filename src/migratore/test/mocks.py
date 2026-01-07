#!/usr/bin/python
# -*- coding: utf-8 -*-


class FakeMigration(object):
    def __init__(self, uuid, timestamp):
        self.uuid = uuid
        self.timestamp = timestamp

    def __str__(self):
        return "Migration(%s, %d)" % (self.uuid, self.timestamp)


class FakeDatabase(object):
    def __init__(self, current_timestamp=0, existing_uuids=None, uuid_results=None):
        self.current_timestamp = current_timestamp
        self.existing_uuids = existing_uuids or set()
        self.uuid_results = uuid_results or {}

    def timestamp(self):
        return self.current_timestamp

    def exist_uuid(self, uuid, result="success"):
        if self.uuid_results:
            return self.uuid_results.get(uuid) == result
        return uuid in self.existing_uuids

    def close(self):
        pass


class FakeTable(object):
    def __init__(self, records=None):
        self.records = records

    def get(self, where=None):
        if self.records == None:
            return None
        if callable(self.records):
            return self.records(where)
        return self.records
