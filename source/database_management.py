import sqlite3

class TableField:
    def __init__(self, name: str, data_type: str, is_primary_key: bool = False):
        self.name = name
        self.data_type = data_type
        self.is_primary_key = is_primary_key
    
class Table:
    def __init__(self, name: str, fields):
        self.name = name
        self.fields = fields

class Account:
    def __init__(self, name, password):
        self.name = name
        self.password = password

def create_table_if_nonexistent_using_cursor(table: Table, cursor):
    """
        Creates the specified database table using a cursor object if the table does not already exist
        table: A database table object
        cursor: A cursor created using a database connection
    """
    creation_text = f"CREATE TABLE IF NOT EXISTS {table.name} ("
    for field in table.fields:
        creation_text += f"{field.name} {field.data_type}"
        if field.is_primary_key:
            creation_text += "PRIMARY KEY"
    cursor.execute(creation_text)

def create_placeholders_for_fields(fields):
    placeholder = "("
    added_placeholder_before = False
    for _ in fields:
        placeholder += "?"
        if added_placeholder_before:
            placeholder += ", "
        placeholder = False
    placeholder += ")"
    return placeholder

def insert_values_into_table_for_database_at_path(values, table: Table, path: str):
    """
        Inserts the values into the specified table for the database at the path.
        This can throw a sqlite3.Error exception!
        values: a tuple of values
        table: a database table object
        path: the path containing the database
    """
    connection = sqlite3.connect(path)
    insertion_command = f"INSERT INTO {table.name} VALUES" + create_placeholders_for_fields(table.fields)
    exception = None
    try:
        with connection:
            connection.execute(insertion_command, values)
    except sqlite3.Error as e:
        exception = e
    connection.close()
    if exception:
        raise exception



ACCOUNT_TABLE = Table('account', [TableField('name', 'TEXT', is_primary_key=True), TableField('password', 'TEXT')])
TABLES = [ACCOUNT_TABLE]

def insert_account_into_database_at_path(account: Account, path: str):
    values = (account.name, account.password)
    insert_values_into_table_for_database_at_path(values, ACCOUNT_TABLE, path)

def create_database_at_path(path: str):
    """
        Creates a database at the specified filepath if nonexistent. If the database exists, any missing tables are added to it.
        path: the path at which to create the database
    """
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    for table in TABLES:
        create_table_if_nonexistent_using_cursor(table, cursor)
    connection.commit()
    connection.close()

