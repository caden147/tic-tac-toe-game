from server import Server, help_messages
import protocol_definitions
from protocol import Message
import connection_handler
import unittest
from testing_utilities import *

def create_text_message(text: str):
    return Message(protocol_definitions.TEXT_MESSAGE_PROTOCOL_TYPE_CODE, {"text": text})

EMPTY_GAME_BOARD = {'text': " "*9}
EMPTY_GAME_BOARD_MESSAGE = Message(protocol_definitions.GAME_UPDATE_PROTOCOL_TYPE_CODE, EMPTY_GAME_BOARD)
PLAYING_X_MESSAGE = Message(protocol_definitions.GAME_PIECE_PROTOCOL_TYPE_CODE, {"character": "X"})
PLAYING_O_MESSAGE = Message(protocol_definitions.GAME_PIECE_PROTOCOL_TYPE_CODE, {"character": "O"})
GAME_CREATION_MESSAGE = create_text_message("The game was created!")

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
            GAME_CREATION_MESSAGE,
            PLAYING_X_MESSAGE,
            EMPTY_GAME_BOARD_MESSAGE
        ]
        testcase = TestCase(should_perform_automatic_login=True)
        testcase.create_client("Bob")
        testcase.buffer_client_commands("Bob", [ReceivedMessagesLengthWaitingCommand(1), "create Alice", ReceivedMessagesLengthWaitingCommand(2), "join Alice"])
        testcase.run()
        testcase.assert_received_values_match_log(expected_messages, 'Bob')
        
    def test_join_and_quit(self):
        testcase = TestCase(should_perform_automatic_login=True)
        testcase.create_client("Bob")
        testcase.create_client("Alice")
        testcase.buffer_client_commands("Bob", [ReceivedMessagesLengthWaitingCommand(1), "create Alice", ReceivedMessagesLengthWaitingCommand(2), "join Alice", ReceivedMessagesLengthWaitingCommand(4), 'quit'])
        testcase.buffer_client_commands("Alice", [ReceivedMessagesLengthWaitingCommand(4)])
        testcase.run()
        expected_alice_messages = [
            SkipItem(),
            create_text_message("Bob invited you to a game!"),
            create_text_message("Bob has joined your game!"),
            create_text_message("Bob has left your game!")
        ]
        testcase.assert_received_values_match_log(expected_alice_messages, "Alice")


if __name__ == '__main__':
    unittest.main()