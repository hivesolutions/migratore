# Migratore Infra-Structure

Simple migration framework / infra-structure for SQL based databases.

## Installation

```bash
easy_install migratore
```

## Execution

```
HOST=$(HOST) DB=$(DB_NAME) USERNAME=$(USERNAME) PASSWORD=$(PASSWORD) migratore.sh upgrade
```

## Commands

* `version` - Prints a help message about the cli interface
* `version` - Prints the current version of migratore
* `list` - Lists the executed migrations on the current database
* `errors` - Lists the various errors from migration of the database
* `upgrade [path]` - Executes the pending migrations using the defined directory or current
* `generate [path]` - Generates a new migration file into the target path

## Examples

```python
database = Migratore.get_database()
table = database.get_table("users")
table.add_column("username", type = "text")
```
