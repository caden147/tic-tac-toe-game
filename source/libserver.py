
import os

import protocol
import protocol_definitions
import logging_utilities
import connection_handler

os.makedirs("logs", exist_ok=True)
logger = logging_utilities.Logger(os.path.join("logs", "server.log"))

help_messages = {
    "": "The server will offer support for tictactoe games in the future. Help topics include\ngameplay\nsetup\n",
    "gameplay": "When the server supports tictactoe games, you submit your move by typing the coordinates for a position and pressing enter.",
    "setup": "When the server supports tictactoe games, you will create a game with the create command and join a game with the join command."
}

protocol_callback_handler = protocol.ProtocolCallbackHandler()
def create_help_message(values):
    label: str = values.get("text", "")
    if label in help_messages:
        return (help_messages[label],)
    else:
        return (f"Did not recognize help topic {label}!\n{help_messages[""]}",)
protocol_callback_handler.register_callback_with_protocol(create_help_message, protocol_definitions.BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE)
protocol_callback_handler.register_callback_with_protocol(create_help_message, protocol_definitions.HELP_MESSAGE_PROTOCOL_TYPE_CODE)

def create_connection_handler(selector, connection, address):
    connection_information = connection_handler.ConnectionInformation(connection, address)
    handler = connection_handler.ConnectionHandler(
        selector,
        connection_information,
        logger,
        protocol_callback_handler, 
        is_server = True
    )
    return handler
