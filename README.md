# [![Migratore](res/logo.png)](http://migratore.hive.pt)

Simple migration framework / infra-structure for SQL-based databases.

## Installation

```bash
pip install migratore
```

## Execution

```bash
HOST=${HOST} DB=${DB_NAME} USERNAME=${DB_USER} PASSWORD=${DB_PASS} migratore upgrade
```

## Variables

* `HOST` - Hostname or IP address of the database system for migration
* `PORT` - TCP port to be used in the connection with the database system
* `UNIX_SOCKET` - Filesystem path to the UNIX socket file to be used in connection
* `DB` - Name of the database used as the migration target
* `USERNAME` - Username for authentication in the database
* `PASSWORD` - Password to be used for authentication in the database
* `FS` - Base file system path for file migration (may depend on migration context)
* `DB_URL` - The database connection URL following the format `protocol://username:password@host:port/db`
* `SAFE` - If the migration operation should be performed in a safe manner.

## Commands

* `help` - Prints a help message about the CLI interface
* `version` - Prints the current version of migratore
* `environ` - Displays the current environment in the standard output
* `list` - Lists the executed migrations on the current database
* `errors` - Lists the various errors from migration of the database
* `mark [path]` - Marks all pending migrations as applied using the defined directory or current
* `trace [id]` - Prints the traceback for the error execution with the provided id
* `rebuild [id]` - Run the partial execution of the migration with the given id
* `touch [id]` - Touches a migration file updating its timestamp to the current time
* `squash [start] [end] <output>` - Combines multiple migrations into a single file
* `upgrade [path]` - Executes the pending migrations using the defined directory or current
* `dry_upgrade [path]` - Prints the pending migrations without executing them
* `downgrade [path]` - Rolls back the last applied migration using the defined directory or current
* `dry_downgrade [path]` - Prints the last applied migration without rolling it back
* `skip [path]` - Skips the current migration (next to be run) using the defined directory or current
* `generate [path]` - Generates a new migration file into the target path

## Operations

Every command that touches a migration records a row in the `migratore` bookkeeping table with an `operation` value that describes what was done. The same migration can have multiple rows over time (e.g. a `Run` followed later by a `Rollback`). The most recent row for each UUID is what determines whether the migration is currently applied.

* `Run` - Normal application of a migration through `upgrade`. Invokes `Migration.run`.
* `Run Partial` - Re-execution of a single migration through `rebuild [id]`. Invokes `Migration.run_partial`, useful for resuming a migration that previously failed mid-way.
* `Run Skip` - Records the migration as applied through `skip` without executing its `run` body. Invokes `Migration.run_skip`. Handy when adopting `migratore` on a database that already has the target schema, or when a migration has been applied out-of-band.
* `Rollback` - Explicit downgrade through `downgrade`, or recovery rollback automatically triggered when a `run` fails (when `SAFE` is `False`). Invokes `Migration.rollback`. The `force` argument distinguishes the two cases: `True` for an explicit downgrade, `False` for recovery.

A migration is considered **currently applied** whenever the most recent successful row for its UUID is anything other than `Rollback`. This means a migration that was rolled back via `downgrade` becomes pending again and will be re-applied by the next `upgrade`.

## Examples

```python
database = Migratore.get_database()
table = database.get_table("users")
table.add_column("username", type = "text")
```

## License

Migratore is currently licensed under the [Apache License, Version 2.0](http://www.apache.org/licenses/).

## Build Automation

[![Build Status](https://github.com/hivesolutions/migratore/workflows/Main%20Workflow/badge.svg)](https://github.com/hivesolutions/migratore/actions)
[![Coverage Status](https://coveralls.io/repos/hivesolutions/migratore/badge.svg?branch=master)](https://coveralls.io/r/hivesolutions/migratore?branch=master)
[![PyPi Status](https://img.shields.io/pypi/v/migratore.svg)](https://pypi.python.org/pypi/migratore)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://www.apache.org/licenses/)
