#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from . import info
from . import migration


def run_help():
    print("%s %s (%s)" % (info.NAME, info.VERSION, info.AUTHOR))
    print("")
    print("  version         Prints the current version of migratore")
    print("  environ         Displays the current environment in the standard output")
    print("  list            Lists the executed migrations on the current database")
    print("  errors          Lists the various errors from migration of the database")
    print(
        "  mark            Marks the associated data source with the current timestamp"
    )
    print(
        "  trace [id]      Prints the traceback for the error execution with the provided id"
    )
    print(
        "  rebuild [id]    Run the partial execution of the migration with the given id"
    )
    print(
        "  upgrade [path]  Executes the pending migrations using the defined directory or current"
    )
    print("  generate [path] Generates a new migration file into the target path")


def run_version():
    print("%s %s" % (info.NAME, info.VERSION))


def run_environ():
    migration.Migration.environ()


def run_list():
    migration.Migration.list()


def run_errors():
    migration.Migration.errors()


def run_mark():
    migration.Migration.mark()


def run_trace(id):
    migration.Migration.trace(id)


def run_rebuild(id):
    migration.Migration.rebuild(id)


def run_upgrade(path=None):
    migration.Migration.upgrade(path)


def run_generate(path=None):
    migration.Migration.generate(path)


def main():
    # validates that the provided number of arguments
    # is the expected one, in case it's not uses the
    # default command as the argument value
    if len(sys.argv) < 2:
        sys.argv.append("help")

    # retrieves the fir
    scope = sys.argv[1]

    # retrieves the set of extra arguments to be sent to the
    # command to be executed, (this may be dangerous)
    args = sys.argv[2:]

    # retrieves the current set of global symbols as the
    # migratore reference, this is going to be the main
    # structure to be used for command resolution
    migratore = globals()

    # tries to retrieve the proper command method using all
    # of the possible strategies and failing with an exception
    # in case none of the retrieval strategies have succeeded
    command = migratore.get(scope, None)
    command = migratore.get("run_" + scope, command)
    if not command:
        raise RuntimeError("Invalid command provided")

    # runs the command that has just been retrieved and with the
    # arguments provided by the command line (as expected)
    command(*args)


if __name__ == "__main__":
    main()
else:
    __path__ = []
