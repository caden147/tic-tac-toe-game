
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
logger = logging_utilities.Logger(os.path.join("logs", "client.log"))

class Message:
    def __init__(self, selector, sock, addr, type_code, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self.initial_type_code = type_code
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self.response = None
        self.message_handler = protocol.MessageHandler(protocol_definitions.CLIENT_PROTOCOL_MAP)
        self.response_type_code = None

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

    def _create_message(
        self
    ):
        message = protocol_definitions.SERVER_PROTOCOL_MAP.pack_values_given_type_code(self.initial_type_code, *self.request)
        return message

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self.response_type_code is None:
            self.process_response_type_code()

        if self.response is None:
            self.process_response()

    def write(self):
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued and not self._send_buffer:
            # Set selector to listen for read events, we're done writing.
            self._set_selector_events_mask("r")

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

    def queue_request(self):
        message = self._create_message()
        self._send_buffer += message
        self._request_queued = True

    def process_response_type_code(self):
        if len(self._recv_buffer) >= protocol.TYPE_CODE_SIZE:
            self.response_type_code = protocol.unpack_type_code_from_message(self._recv_buffer)
            self._recv_buffer = protocol.compute_message_after_type_code(self._recv_buffer)
            self.message_handler.update_protocol(self.response_type_code)

    def process_response(self):
        is_done = False
        if protocol_definitions.CLIENT_PROTOCOL_MAP.get_protocol_with_type_code(self.response_type_code).get_number_of_fields() == 0:
            is_done = True
            self.response = {}
        else:
            self.message_handler.receive_bytes(self._recv_buffer)
            if self.message_handler.is_done_obtaining_values():
                is_done = True
                self.response = self.message_handler.get_values()
            else:
                self._recv_buffer = b""
        if is_done:
            print("received response with type code", self.response_type_code, repr(self.response), "from", self.addr)
            # Close when response has been processed
            self.close()
