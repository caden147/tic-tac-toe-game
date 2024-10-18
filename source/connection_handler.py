import selectors

import protocol
import protocol_definitions

class ConnectionInformation:
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr

class MessageSender:
    def __init__(self, logger, connection_information: ConnectionInformation, protocol_map, close_callback):
        self.logger = logger
        self.sock = connection_information.sock
        self.addr = connection_information.addr
        self.buffer = b""
        self.request_queued = False
        self.protocol_map = protocol_map
        self.close_callback = close_callback
    
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
                self.close_callback()
            else:
                self.buffer = self.buffer[sent:]

    def send_message(self, type_code, values):
        message = self.protocol_map.pack_values_given_type_code(type_code, *values)
        self.buffer += message
        self._request_queued = True
        self.write()

class Message:
    def __init__(self, type_code, values):
        self.type_code = type_code
        self.values = values

class MessageReceiver:
    def __init__(self, logger, connection_information: ConnectionInformation, message_handler: protocol.MessageHandler, close_callback):
        self.logger = logger
        self.sock = connection_information.sock
        self.addr = connection_information.addr
        self.message_handler: protocol.MessageHandler = message_handler
        self.buffer = b""
        self.request = None
        self.requests = []
        self.close_callback = close_callback

    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(4096)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        except OSError as exception:
            print('Error: A Connection Failure Occurred!')
            self.logger.log_message(f"{exception} trying to connect to {self.addr}")
            self.close_callback()
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
            request = Message(type_code, values)
            self.requests.append(request)
        else:
            self.buffer = b""
        content_length = self.message_handler.get_number_of_bytes_extracted()
        if is_done:
            if len(self.buffer) > 0:
                self.buffer = self.buffer[content_length:]
            print("received request with type code", self.request_type_code, repr(self.request), "from", self.addr)

    def has_processed_requests(self):
        return len(self.requests) > 0

    def extract_request(self) -> Message:
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
        self.message_sender = MessageSender(self.connection_information, sending_protocol_map, self.close)
        self.callback_handler = callback_handler
        message_handler = protocol.MessageHandler(receiving_protocol_map)
        self.message_receiver = MessageReceiver(self.logger, connection_information, message_handler, self.close)
        self.logger = logger

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

    def send_response_to_request(self, request: Message):
        message_values = self.callback_handler.pass_values_to_protocol_callback(self.request.values, request.type_code)
        if self.is_server:
            response = Message(request.type_code, *message_values)
            self.send_message(response)

    def respond_to_request(self):
        request = self.message_receiver.extract_request()
        if self.callback_handler.has_protocol(request.type_code):
            self.send_response_to_request(request)
        
    def read(self):
        self.message_receiver.read()
        while self.message_receiver.has_processed_requests():
            self.respond_to_request()

    def send_message(self, request: Message):
        self.message_sender.send_message(request.type_code, request.values)

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.message_sender.write()
    
    def close(self):
        self.logger.log_message(f"closing connection to {self.addr}")
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            self.logger.log_message(f"error: selector.unregister() exception for {self.addr}: {repr(e)}")
        try:
            self.sock.close()
        except OSError as e:
            self.logger.log_message(f"error: socket.close() exception for {self.addr}: {repr(e)}")
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None
        
    