from server import Server, help_messages
import protocol_definitions
from protocol import Message
import connection_handler
import unittest
from testing_utilities import *


class TestMocking(unittest.TestCase):
    def test_can_send_messages_back_and_forth(self):
        expected_message = Message(0, {'text': help_messages[""]})
        testcase = TestCase()
        testcase.create_client("Bob")
        testcase.buffer_client_command("Bob", "help")
        testcase.buffer_client_command("Bob", ReceivedMessagesLengthWaitingCommand(1))
        testcase.run()
        output = testcase.get_output("Bob")
        print('output', output)
        testcase.assert_received_values_match_log([expected_message], 'Bob')
        testcase.assert_values_match_output([ContainsMatcher("Help")], 'Bob')

if __name__ == '__main__':
    unittest.main()