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

    def test_game_creation(self):
        expected_messages = [
            SkipItem(), 
            Message(protocol_definitions.TEXT_MESSAGE_PROTOCOL_TYPE_CODE, {"text": "The game was created!"}),
            Message(protocol_definitions.GAME_PIECE_PROTOCOL_TYPE_CODE, {"character": "X"}),
            Message(protocol_definitions.GAME_UPDATE_PROTOCOL_TYPE_CODE, {'text': " "*9})
        ]
        testcase = TestCase(should_perform_automatic_login=True)
        testcase.create_client("Bob")
        testcase.buffer_client_commands("Bob", [ReceivedMessagesLengthWaitingCommand(1), "create Alice", ReceivedMessagesLengthWaitingCommand(2), "join Alice"])
        testcase.run()
        testcase.assert_received_values_match_log(expected_messages, 'Bob')
        

if __name__ == '__main__':
    unittest.main()