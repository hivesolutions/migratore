# [Migratore](http://migratore.hive.pt)

Simple migration framework / infra-structure for SQL based databases.

## Installation

```bash
pip install migratore
```

## Execution

```
HOST=${DB_HOST} DB=${DB_NAME} USERNAME=${DB_USER} PASSWORD=${DB_PASSWORD} migratore upgrade
```

## Variables

* `HOST` - Hostname or IP address of the database system for migration
* `DB` - Name of the database used as the migration target
* `USERNAME` - Username for authentication in database
* `USERNAME` - Password to be used for authentication in database
* `FS` - Base file system path for file migration (may depend on migration context)

## Commands

* `help` - Prints a help message about the cli interface
* `version` - Prints the current version of migratore
* `environ` - Displays the current environment in the standard output
* `list` - Lists the executed migrations on the current database
* `errors` - Lists the various errors from migration of the database
* `trace [id]` - Prints the traceback for the error execution with the provided id
* `rebuild [id]` - Run the partial execution of the migration with the given id
* `upgrade [path]` - Executes the pending migrations using the defined directory or current
* `generate [path]` - Generates a new migration file into the target path

## Examples

```python
database = Migratore.get_database()
table = database.get_table("users")
table.add_column("username", type = "text")
```
