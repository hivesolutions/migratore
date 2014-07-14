# [Migratore](http://migratore.hive.pt)

Simple migration framework / infra-structure for SQL based databases.

## Installation

```bash
pip install migratore
```

## Execution

```
HOST=$(HOST) DB=$(DB_NAME) USERNAME=$(USERNAME) PASSWORD=$(PASSWORD) migratore.sh upgrade
```

## Commands

* `help` - Prints a help message about the cli interface
* `version` - Prints the current version of migratore
* `environ` - Displays the current environment in the standard output
* `list` - Lists the executed migrations on the current database
* `errors` - Lists the various errors from migration of the database
* `trace [id]` - Prints the traceback for the error execution with the provided id
* `upgrade [path]` - Executes the pending migrations using the defined directory or current
* `generate [path]` - Generates a new migration file into the target path

## Examples

```python
database = Migratore.get_database()
table = database.get_table("users")
table.add_column("username", type = "text")
```
