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
* `trace [id]` - Prints the traceback for the error execution with the provided id
* `rebuild [id]` - Run the partial execution of the migration with the given id
* `upgrade [path]` - Executes the pending migrations using the defined directory or current
* `skip [path]` - Skips the current migration (next to be run) using the defined directory or current
* `generate [path]` - Generates a new migration file into the target path

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
