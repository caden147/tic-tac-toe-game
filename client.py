
#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import os
from threading import Thread

import connection_handler
import logging_utilities
import protocol_definitions
import protocol
import game_actions

sel = selectors.DefaultSelector()
os.makedirs("logs", exist_ok=True)
logger = logging_utilities.Logger(os.path.join("logs", "client.log"))
current_game = None
protocol_callback_handler = protocol.ProtocolCallbackHandler()

def update_game(values):
    global current_game
    current_game = values["text"]
    print("The game board is now:")
    print(current_game)
protocol_callback_handler.register_callback_with_protocol(update_game, protocol_definitions.GAME_UPDATE_PROTOCOL_TYPE_CODE)

def create_connection(host, port):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    connection = connection_handler.ConnectionHandler(
        sel,
        connection_handler.ConnectionInformation(sock, addr),
        logger,
        protocol_callback_handler,
    )
    sel.register(sock, events, data=connection)
    return connection

def _parse_two_space_separated_values(text):
    """Parses text into 2 space separated values. Returns None on failure."""
    values = text.split(" ", maxsplit=1)
    if len(values) != 2:
        return None
    return values

def create_request(action, value):
    """Creates a request for the server from an action value pair"""
    type_code = None
    values = None
    request = None
    if action == "help":
        if value:
            type_code = protocol_definitions.HELP_MESSAGE_PROTOCOL_TYPE_CODE
            values = (value,)
        else:
            type_code = protocol_definitions.BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE
            values = []
    elif action == "login":
        values = _parse_two_space_separated_values(value)
        if values is not None:
            type_code = protocol_definitions.SIGN_IN_PROTOCOL_TYPE_CODE
    elif action == "register":
        values = _parse_two_space_separated_values(value)
        if values is not None:
            type_code = protocol_definitions.ACCOUNT_CREATION_PROTOCOL_TYPE_CODE
    elif action == "quit":
        if current_game is not None:
            type_code = protocol_definitions.QUIT_GAME_PROTOCOL_TYPE_CODE
    elif action == "join":
        if value != "" and current_game is None:
            type_code = protocol_definitions.JOIN_GAME_PROTOCOL_TYPE_CODE
            values = (value,)
    elif action == "create" and current_game is None:
        if value != "":
            type_code = protocol_definitions.GAME_CREATION_PROTOCOL_TYPE_CODE
            values = (value,)
    elif action == "move":
        if current_game is not None and game_actions.is_valid_move_text(value):
            type_code = protocol_definitions.GAME_UPDATE_PROTOCOL_TYPE_CODE
            move_number = game_actions.convert_move_text_to_move_number(value)
            values = (move_number,)

    if type_code is not None:
        request = protocol.Message(type_code, values)
    return request

def create_request_from_text_input(text: str):
    """Creates a request for the server from user input text"""
    text = text.strip()
    action_value_split = text.split(' ', maxsplit=1)
    action = action_value_split[0]
    value = ""
    #If an argument is detected for the action, put it inside value
    if len(action_value_split) > 1:
        value = action_value_split[1]
    request = create_request(action, value)
    return request

def perform_user_commands_through_connection(connection_handler: connection_handler.ConnectionHandler):
    done = False
    while not done:
        user_input = input('')
        if user_input == 'exit':
            done = True
        else:
            request = create_request_from_text_input(user_input)
            if request is None:
                print('Command not recognized.')
            else:
                connection_handler.send_message(request)
    connection_handler.close()

if len(sys.argv) != 3:
    print("usage:", sys.argv[0], "<host> <port>")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])


connection = create_connection(host, port)
#Run the client input loop in a separate thread
client_input_thread = Thread(target=perform_user_commands_through_connection, args=(connection,))
client_input_thread.start()


try:
    while True:
        events = sel.select(timeout=None)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                logger.log_message(
                    f"main: error: exception for {message.connection_information.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
