from server import Server, help_messages
from client import Client
from mock_socket import MockInternet, MockSelector, MockListeningSocket, MockTCPSocket
from logging_utilities import PrimaryMemoryLogger
import protocol_definitions
from protocol import Message
import connection_handler
import unittest
from testing_utilities import *


class TestMocking(unittest.TestCase):
    def test_can_send_messages_back_and_forth(self):
        server_address = ('localhost', 9090)
        expected_message_event = connection_handler.MessageEvent(Message(0, {'text': help_messages[""]}), server_address)
        testcase = TestCase(server_address[0], server_address[1])
        testcase.create_client("Bob")
        testcase.buffer_client_command("Bob", "help")
        testcase.buffer_client_command("Bob", ReceivedMessagesLengthWaitingCommand(1))
        testcase.run()
        results = testcase.get_log("Bob", connection_handler.RECEIVING_MESSAGE_LOG_CATEGORY)
        output = testcase.get_output("Bob")
        print('output', output)
        actual_message_event = results[0]
        print('results', results)
        self.assertEqual(expected_message_event, actual_message_event)

if __name__ == '__main__':
    unittest.main()