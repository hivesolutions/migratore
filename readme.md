# Migratore Infra-Structure

Simple migration frmework / infra-structure for the 

## Examples

```python
database = Migratore.get_database()
table = database.get_table("users")
table.add_column("username", type = "text")
```