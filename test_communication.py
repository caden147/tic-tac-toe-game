from server import Server, help_messages
from client import Client
from mock_socket import MockInternet, MockSelector, MockListeningSocket, MockTCPSocket
from logging_utilities import PrimaryMemoryLogger
import protocol_definitions
from protocol import Message
import connection_handler
import time
import unittest
from threading import Thread
from testing_utilities import *


class TestMocking(unittest.TestCase):
    def test_can_send_messages_back_and_forth(self):
        server_address = ('localhost', 9090)
        expected_message_event = connection_handler.MessageEvent(Message(0, {'text': help_messages[""]}), server_address)
        factory = TestingFactory('localhost', 9090)
        server = factory.create_server()
        try:
            server.listen_for_socket_events_without_blocking()
            client = factory.create_client()
            client.send_message(Message(protocol_definitions.BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE, []))
            client.run_selector_loop_without_blocking()
            wait_until_true_or_timeout(lambda: len(client.get_log(connection_handler.RECEIVING_MESSAGE_LOG_CATEGORY)) > 0)
            client.close()
            server.close()
        except Exception as exception:
            server.close()
            client.close()
            raise exception
        results = client.get_log(connection_handler.RECEIVING_MESSAGE_LOG_CATEGORY)
        actual_message_event = results[0]
        print('results', results)
        self.assertEqual(expected_message_event, actual_message_event)

if __name__ == '__main__':
    unittest.main()