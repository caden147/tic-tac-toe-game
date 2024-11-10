from server import Server, help_messages
import protocol_definitions
from protocol import Message
import connection_handler
import unittest
from testing_utilities import *


class TestMocking(unittest.TestCase):
    def test_can_send_messages_back_and_forth(self):
        expected_message_event = connection_handler.MessageEvent(Message(0, {'text': help_messages[""]}), TestCase.DEFAULT_SERVER_ADDRESS)
        testcase = TestCase()
        testcase.create_client("Bob")
        testcase.buffer_client_command("Bob", "help")
        testcase.buffer_client_command("Bob", ReceivedMessagesLengthWaitingCommand(1))
        testcase.run()
        output = testcase.get_output("Bob")
        print('output', output)
        testcase.assert_values_match_log(self, [expected_message_event], 'Bob', connection_handler.RECEIVING_MESSAGE_LOG_CATEGORY)

if __name__ == '__main__':
    unittest.main()