from server import Server
from client import Client
from mock_socket import MockInternet, MockSelector, MockListeningSocket, MockTCPSocket
from logging_utilities import PrimaryMemoryLogger
import protocol_definitions
from protocol import Message

import unittest
from threading import Thread


class TestMocking(unittest.TestCase):
    def test_can_send_messages_back_and_forth(self):
        client_logger = PrimaryMemoryLogger()
        server_logger = PrimaryMemoryLogger()
        internet = MockInternet()
        client_selector = MockSelector()
        server_selector = MockSelector()
        client_output = []
        client = Client('200', 19, client_selector, client_logger, output_text_function=lambda x: client_output.append(x), socket_creation_function=internet.create_socket_from_address)
        server = Server('localhost', 9090, server_selector, server_logger, 'testing.db', internet.create_listening_socket_from_address)
        server_listening_thread = Thread(target=server.listen_for_socket_events)
        try:
            server_listening_thread.start()
            client.send_message(Message(protocol_definitions.BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE, []))
        except Exception as exception:
            server.close()
            raise exception

if __name__ == '__main__':
    unittest.main()