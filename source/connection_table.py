from connection_handler import ConnectionHandler, ConnectionInformation
from protocol import Message

class ConnectionTableEntry:
    def __init__(self, connection_handler: ConnectionHandler, state):
        self.connection_handler = connection_handler
        self.state = state

    def compute_table_representation(self):
        connection_information = self.connection_handler.get_connection_information()
        return connection_information.text_representation

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

    def remove_entry(self, connection_information: ConnectionInformation):
        representation = connection_information.text_representation
        if representation in self.connections:
            self.connections.pop(connection_information.text_representation)

    def get_entry(self, connection_information: ConnectionInformation):
        return self.connections.get(connection_information.text_representation, None)

    def send_message_to_entry(self, message: Message, connection_information: ConnectionInformation):
        entry = self.get_entry(connection_information)
        if entry is not None:
            entry.send_message_through_connection(message)