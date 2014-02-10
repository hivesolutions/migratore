# Migratore Infra-Structure

Simple migration framework / infra-structure for SQL based databases.

## Examples

```python
database = Migratore.get_database()
table = database.get_table("users")
table.add_column("username", type = "text")
```
