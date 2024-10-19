from connection_handler import ConnectionHandler, ConnectionInformation, compute_unique_connection_information_representation
from protocol import Message

class ConnectionTableEntry:
    def __init__(self, connection_handler: ConnectionHandler, state):
        self.connection_handler = connection_handler
        self.state = state

    def compute_table_representation(self):
        connection_information = self.connection_handler.get_connection_information()
        representation = compute_unique_connection_information_representation(connection_information)
        return representation

    def send_message_through_connection(self, message: Message):
        self.connection_handler.send_message(message)

    def get_state(self):
        return self.state

class ConnectionTable:
    def __init__(self):
        self.connections = {}

    def insert_entry(self, entry: ConnectionTableEntry):
        representation = entry.compute_table_representation()
        self.connections[representation] = entry

    def remove_entry(self, entry: ConnectionTableEntry):
        representation = entry.compute_table_representation()
        self.connections.pop(representation)

    def get_entry(self, connection_information: ConnectionInformation):
        representation = compute_unique_connection_information_representation(connection_information)
        return self.connections.get(representation, None)

    