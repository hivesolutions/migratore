#!/usr/bin/python
# -*- coding: utf-8 -*-

import info
import migration

def run_help():
    print "%s %s (%s)" % (info.NAME, info.VERSION, info.AUTHOR)
    print ""
    print "  version         Prints the current version of migratore"
    print "  environ         Displays the current environment in the standard output"
    print "  list            Lists the executed migrations on the current database"
    print "  errors          Lists the various errors from migration of the database"
    print "  trace [id]      Prints the traceback for the error execution with the provided id"
    print "  upgrade [path]  Executes the pending migrations using the defined directory or current"
    print "  generate [path] Generates a new migration file into the target path"

def run_version():
    print "%s %s" % (info.NAME, info.VERSION)

def run_environ():
    migration.Migration.environ()

def run_list():
    migration.Migration.list()

def run_errors():
    migration.Migration.errors()

def run_trace(id):
    migration.Migration.trace(id)

def run_upgrade(path = None):
    migration.Migration.upgrade(path)

def run_generate(path = None):
    migration.Migration.generate(path)
