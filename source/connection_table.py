from connection_handler import ConnectionHandler, ConnectionInformation
from protocol import Message

class ConnectionTableEntry:
    def __init__(self, connection_handler: ConnectionHandler, state):
        """
            Contains information associated with a connection
            connection_handler: the ConnectionHandler for communicating through the connection
            state: information to associate with the connection
        """
        self.connection_handler = connection_handler
        self.state = state

    def compute_table_representation(self):
        """Computes a unique text representation of the connection"""
        connection_information = self.connection_handler.get_connection_information()
        return connection_information.text_representation

    def send_message_through_connection(self, message: Message):
        """Sends the Message object the the connection"""
        self.connection_handler.send_message(message)

    def get_state(self):
        """Return state information associated with the connection"""
        return self.state

class ConnectionTable:
    def __init__(self):
        """A table for keeping track of connections"""
        self.connections = {}

    def insert_entry(self, entry: ConnectionTableEntry):
        """Adds the ConnectionTableEntry to the table"""
        representation = entry.compute_table_representation()
        self.connections[representation] = entry

    def remove_entry(self, connection_information: ConnectionInformation):
        """Removes the entry with specified ConnectionInformation from the table if present and otherwise fails silently"""
        representation = connection_information.text_representation
        if representation in self.connections:
            self.connections.pop(connection_information.text_representation)

    def get_entry(self, connection_information: ConnectionInformation):
        """Returns the ConnectionTableEntry corresponding to the ConnectionInformation"""
        return self.connections.get(connection_information.text_representation, None)

    def get_entry_state(self, connection_information: ConnectionInformation):
        """Returns the state information associated with the ConnectionInformation"""
        entry = self.get_entry(connection_information)
        state = entry.get_state()
        return state

    def send_message_to_entry(self, message: Message, connection_information: ConnectionInformation):
        """Sends the message through the connection associated with the connection information if present and otherwise fails silently"""
        entry = self.get_entry(connection_information)
        if entry is not None:
            entry.send_message_through_connection(message)