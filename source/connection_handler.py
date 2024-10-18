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

class ConnectionHandler:
    def __init__(self, selector, connection_information: ConnectionInformation, logger, *, is_server: bool=False):
        self.selector = selector
        self.connection_information = connection_information
        if is_server:
            sending_protocol_map = protocol_definitions.CLIENT_PROTOCOL_MAP
            receiving_protocol_map = protocol_definitions.SERVER_PROTOCOL_MAP
        else:
            sending_protocol_map = protocol_definitions.SERVER_PROTOCOL_MAP
            receiving_protocol_map = protocol_definitions.CLIENT_PROTOCOL_MAP
        self.message_sender = MessageSender(self.connection_information, sending_protocol_map)
        self.is_server = is_server
        self.logger = logger
