### Database Source Files
## `db_connection.py`
Holds a stateful connection to the DB accessible to all other python modules
through `db.connection.connection`. This allows all files to maintain a
connection, avoiding connecting to the database with every API call.

## `query_tables.py`
