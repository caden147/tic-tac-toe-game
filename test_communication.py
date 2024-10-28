from server import Server
from client import Client, run_selector_loop
from mock_socket import MockInternet, MockSelector, MockListeningSocket, MockTCPSocket
from logging_utilities import PrimaryMemoryLogger
import protocol_definitions
from protocol import Message
import connection_handler

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
        server_address = ('localhost', 9090)
        server = Server('localhost', 9090, server_selector, server_logger, 'testing.db', internet.create_listening_socket_from_address)
        server_listening_thread = Thread(target=server.listen_for_socket_events)
        try:
            server_listening_thread.start()
            client = Client('200', 19, client_selector, client_logger, output_text_function=lambda x: client_output.append(x), socket_creation_function= lambda x: internet.create_socket_from_address(x, server_address))
            client.send_message(Message(protocol_definitions.BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE, []))
            run_selector_loop(client_selector, client_logger)
            server.close()
        except Exception as exception:
            server.close()
            raise exception
        results = client_logger.get_log(connection_handler.RECEIVING_MESSAGE_LOG_CATEGORY)
        print('results', results)

if __name__ == '__main__':
    unittest.main()