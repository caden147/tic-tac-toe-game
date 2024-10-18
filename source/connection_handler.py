import selectors
import os

import protocol
import protocol_definitions
import logging_utilities

class ConnectionInformation:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr



class MessageSender:
    def __init__(self, connection_information: ConnectionInformation, protocol_map):
        self.sock = connection_information.sock
        self.addr = connection_information.addr
        self.buffer = b""
        self.request_queued = False
        self.protocol_map = protocol_map
    
    def write(self):
        if self.buffer:
            self.logger.log_message(f"sending {repr(self.buffer)} to {self.addr}")
            try:
                # Should be ready to write
                sent = self.sock.send(self.buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            except OSError as exception:
                print("Error: A Connection Failure Occurred!")
                self.logger.log_message(f"{exception} trying to connect to {self.addr}")
                self.close()
            else:
                self.buffer = self.buffer[sent:]

    def send_message(self, type_code, values):
        message = self.protocol_map.pack_values_given_type_code(type_code, *values)
        self.buffer += message
        self._request_queued = True

class Request:
    def __init__(self, type_code, values):
        self.type_code = type_code
        self.values = values

class MessageReceiver:
    def __init__(self, connection_information: ConnectionInformation, message_handler: protocol.MessageHandler):
        self.sock = connection_information.sock
        self.addr = connection_information.addr
        self.message_handler: protocol.MessageHandler = message_handler
        self.buffer = b""
        self.request = None
        self.requests = []

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self.buffer += data
            else:
                raise RuntimeError("Peer closed.")
    
    def read(self):
        self._read()
        
    def process_request(self):
        is_done = False
        self.message_handler.receive_bytes(self.buffer)
        if self.message_handler.is_done_obtaining_values():
            is_done = True
            values = self.message_handler.get_values()
            type_code = self.message_handler.get_protocol_type_code()
            self.message_handler.prepare_for_next_message()
        else:
            self.buffer = b""
        content_length = self.message_handler.get_number_of_bytes_extracted()
        if is_done:
            if len(self.buffer) > 0:
                self.buffer = self.buffer[content_length:]
            print("received request with type code", self.request_type_code, repr(self.request), "from", self.addr)
            request = Request(type_code, values)
            self.requests.append(request)

    def has_processed_requests(self):
        return len(self.requests) > 0

    def extract_request(self):
        request = self.requests.pop(0)
        return request

class ConnectionHandler:
    def __init__(self, selector, connection_information: ConnectionInformation, logger, callback_handler, *, is_server: bool=False):
        self.selector = selector
        self.connection_information = connection_information
        self.is_server = is_server
        if self.is_server:
            sending_protocol_map = protocol_definitions.CLIENT_PROTOCOL_MAP
            receiving_protocol_map = protocol_definitions.SERVER_PROTOCOL_MAP
        else:
            sending_protocol_map = protocol_definitions.SERVER_PROTOCOL_MAP
            receiving_protocol_map = protocol_definitions.CLIENT_PROTOCOL_MAP
        self.message_sender = MessageSender(self.connection_information, sending_protocol_map)
        self.callback_handler = callback_handler
        message_handler = protocol.MessageHandler(receiving_protocol_map)
        self.message_receiver = MessageReceiver(connection_information, message_handler, callback_handler)
        self.logger = logger


