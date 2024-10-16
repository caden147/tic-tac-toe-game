#This module provides functions for interfacing with the database and classes for encapsulating database entries
#search for the comment starting with "The public interface" for functions intended to be used outside this module

import sqlite3

#Classes for representing database tables

class TableField:
    """Represents one of the values in a table entry"""
    def __init__(self, name: str, data_type: str, is_primary_key: bool = False):
        """
            name: the name of the field
            data_type: the data type of the field as understood by the database
            is_primary_key: determines if this is the primary key for the table
        """
        self.name = name
        self.data_type = data_type
        self.is_primary_key = is_primary_key

class Table:
    """Represents a database table consisting of rows with specific fields"""
    def __init__(self, name: str, fields):
        """
            name: the name of the table
            fields: and ordered iterable of the fields every entry in this table must have
        """
        self.name = name
        self.fields = fields
        self.primary_key = None
        for field in fields:
            if field.is_primary_key:
                self.primary_key = field
                break

# Database entry representation classes
class Account:
    """Represents a user account"""
    def __init__(self, name, password):
        """
            name: the user name associated with the account
            password: the user's password
        """
        self.name = name
        self.password = password

#Database management helper functions. Other modules should not call these.

def _create_table_if_nonexistent_using_cursor(table: Table, cursor):
    """
        Creates the specified database table using a cursor object if the table does not already exist
        table: A database table object
        cursor: A cursor created using a database connection
    """
    creation_text = f"CREATE TABLE IF NOT EXISTS {table.name} ("
    field_already_added = False
    for field in table.fields:
        if field_already_added:
            creation_text += ", "
        creation_text += f"{field.name} {field.data_type}"
        if field.is_primary_key:
            creation_text += " PRIMARY KEY"
        field_already_added = True
    creation_text += ")"
    cursor.execute(creation_text)

def _create_placeholders_for_fields(fields):
    """
        Creates the placeholder text for the specified fields
        fields: an iterable of TableField objects
    """
    placeholder = "("
    added_placeholder_before = False
    for _ in fields:
        if added_placeholder_before:
            placeholder += ", "
        placeholder += "?"
        added_placeholder_before = True
    placeholder += ")"
    return placeholder

def _insert_values_into_table_for_database_at_path(values, table: Table, path: str):
    """
        Inserts the values into the specified table for the database at the path.
        This can throw a sqlite3.Error exception!
        values: a tuple of values
        table: a database table object
        path: the path containing the database
    """
    connection = sqlite3.connect(path)
    insertion_command = f"INSERT INTO {table.name} VALUES" + _create_placeholders_for_fields(table.fields)
    exception = None
    try:
        with connection:
            connection.execute(insertion_command, values)
    except sqlite3.Error as e:
        exception = e
    connection.close()
    if exception:
        raise exception

def _retrieve_values_from_table_from_database_at_path_using_primary_key(table: Table, path: str, primarykey):
    """
        Returns values from a table at the specified database path associated with the primary key if present or otherwise returns None
        table: the table in the database to retrieve values from
        path: the path to the database
        primarykey: the primary key value used to identify the target row in the database
    """
    connection = sqlite3.connect(path)
    retrieval_command = f"SELECT * FROM {table.name} WHERE {table.primary_key.name} = ?"
    cursor = connection.cursor()
    queryresult = cursor.execute(retrieval_command, (primarykey,))
    values = queryresult.fetchone()
    return values

#Database table representation definitions
ACCOUNT_TABLE = Table('account', [TableField('name', 'TEXT', is_primary_key=True), TableField('password', 'TEXT')])
TABLES = [ACCOUNT_TABLE]

#The public interface: functions intended to be used by other modules

def insert_account_into_database_at_path(account: Account, path: str):
    """
        Inserts the account object into the database at the specified path.
        Raises an sqlite3.Error exception if the account already exists.
        account: an Account object
        path: the path to the database
    """
    values = (account.name, account.password)
    _insert_values_into_table_for_database_at_path(values, ACCOUNT_TABLE, path)

def retrieve_account_with_name_from_database_at_path(name: str, path: str):
    values = _retrieve_values_from_table_from_database_at_path_using_primary_key(ACCOUNT_TABLE, path, name)
    result = None
    if values:
        result = Account(*values)
    return result

def create_database_at_path(path: str):
    """
        Creates a database at the specified filepath if nonexistent. If the database exists, any missing tables are added to it.
        path: the path at which to create the database
    """
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    for table in TABLES:
        _create_table_if_nonexistent_using_cursor(table, cursor)
    connection.commit()
    connection.close()

#Simple testing script that assumes that testing.db did not previously exist

if __name__ == '__main__':
    database_path = 'testing.db'
    create_database_at_path(database_path)
    insert_account_into_database_at_path(Account('name', 'password'), database_path)
    result = retrieve_account_with_name_from_database_at_path('name', database_path)
    print('result', result)
    if result is not None:
        print(result.name, result.password)
    empty_result = retrieve_account_with_name_from_database_at_path('george', database_path)
    print('empty_result', empty_result)