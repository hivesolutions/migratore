#!/usr/bin/python
# -*- coding: utf-8 -*-

import info
import migration

def run_help():
    print "%s %s (%s)" % (info.NAME, info.VERSION, info.AUTHOR)
    print ""
    print "The most commonly used migratore commands are:"
    print "  version         Prints the current version of migratore"
    print "  list            Lists the executed migrations on the current database"
    print "  errors          Lists the various errors from migration of the database"
    print "  upgrade [path]  Executes the pending migrations using the defined directory or current"
    print "  generate [path] Generates a new migration file into the target path"

def run_version():
    print "%s %s" % (info.NAME, info.VERSION)

def run_list():
    migration.Migration.list()

def run_errors():
    migration.Migration.errors()

def run_upgrade(path = None):
    migration.Migration.upgrade(path)

def run_generate(path = None):
    migration.Migration.generate(path)
