#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
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

def main():
    # validates that the provided number of arguments
    # is the expected one, in case it's not raises a
    # runtime error indicating the problem
    if len(sys.argv) < 2: raise RuntimeError("Invalid number of arguments")

    # retrieves the fir
    scope = sys.argv[1]

    # retrieves the set of extra arguments to be sent to the
    # command to be executed, (this may be dangerous)
    args = sys.argv[2:]

    # retrieves the current set of global symbols as the
    # migratore reference, this is going to be the main
    # structure to be used for command resolution
    migratore = globals()

    # retrieves both the loader command for the current
    # scope and then uses it to execute the command with
    # the extra arguments as the passing value
    is_command = hasattr(migratore, "run_" + scope)
    if is_command: command = getattr(migratore, "run_" + scope)
    else: command = getattr(migratore, scope)
    command(*args)

if __name__ == "__main__":
    main()
