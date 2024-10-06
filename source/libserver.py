
import sys
import selectors
import json
import io
import struct
import os

import protocol
import protocol_definitions
import logging_utilities

os.makedirs("logs", exist_ok=True)
logger = logging_utilities.Logger(os.path.join("logs", "server.log"))

help_messages = {
    "": "The server will offer support for tictac to games in the future. Help topics include\ngameplay\nsetup\n",
    "gameplay": "When the server supports tictactoe games, you submit your move by typing the coordinates for a position and pressing enter.",
    "setup": "When the server supports tictactoe games, you will create a game with the create command and join a game with the join command."
}

protocol_callback_handler = protocol.ProtocolCallbackHandler()
def create_help_message(label: str = ""):
    if label in help_messages:
        return (help_messages[label],)
    else:
        return (f"Did not recognize help topic {label}!\n{help_messages[""]}",)
protocol_callback_handler.register_callback_with_protocol(create_help_message, protocol_definitions.BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE)
protocol_callback_handler.register_callback_with_protocol(create_help_message, protocol_definitions.HELP_MESSAGE_PROTOCOL_TYPE_CODE)

class Message:
    def __init__(self, selector, sock, addr):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self.request_type_code
        self.request = None
        self.message_handler = protocol.MessageHandler(protocol_definitions.SERVER_PROTOCOL_MAP)
        self.response_created = False

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                raise RuntimeError("Peer closed.")

    def _write(self):
        if self._send_buffer:
            logger.log_message(f"sending {repr(self._send_buffer)} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()

    def _create_message(
        self, *, type_code, content_bytes
    ):
        message = protocol_definitions.CLIENT_PROTOCOL_MAP.pack_values_given_type_code(type_code, content_bytes)
        return message

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self.request_type_code is None:
            self.process_request_type_code()

        if self.request is None:
            self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def close(self):
        logger.log_message(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            logger.log_message(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        try:
            self.sock.close()
        except OSError as e:
            logger.log_message(f"error: socket.close() exception for {self.addr}: {repr(e)}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def process_request_type_code(self):
        if len(self._recv_buffer) >= protocol.TYPE_CODE_SIZE:
            self.request_type_code = protocol.unpack_type_code_from_message(self._recv_buffer)
            self._recv_buffer = protocol.compute_message_after_type_code(self.request_type_code)
            self.message_handler.update_protocol(self.request_type_code)

    def process_request(self):
        is_done = False
        if protocol_definitions.SERVER_PROTOCOL_MAP.get_protocol_with_type_code(self.request_type_code).get_number_of_fields() == 0:
            is_done = True
            self.request = {}
        else:
            self.message_handler.receive_bytes(self._recv_buffer)
            if self.message_handler.is_done_obtaining_values():
                is_done = True
                self.request = self.message_handler.get_values()
            else:
                self._recv_buffer = b""
        content_length = self.message_handler.get_number_of_bytes_extracted()
        if is_done:
            if len(self._recv_buffer) > 0:
                self._recv_buffer = self._recv_buffer[content_length:]
            print("received request with type code", self.request_type_code, repr(self.request), "from", self.addr)
            # Set selector to listen for write events, we're done reading.
            self._set_selector_events_mask("w")

    def create_response(self):
        message_values = protocol_callback_handler.pass_values_to_protocol_callback(self.request, self.request_type_code)
        message = protocol_definitions.CLIENT_PROTOCOL_MAP.pack_values_given_type_code(self.request_type_code, message_values)
        self.response_created = True
        self._send_buffer += message
