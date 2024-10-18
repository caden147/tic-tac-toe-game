import selectors

import protocol
import protocol_definitions

class ConnectionInformation:
    """Class for keeping track of a socket and address"""
    def __init__(self, sock, addr):
        self.sock = sock
        self.addr = addr

class MessageSender:
    def __init__(self, logger, connection_information: ConnectionInformation, protocol_map, close_callback):
        """A message sender is responsible for transmitting a message as bytes to a connection peer
            logger: a logger object for logging errors and significant occurrences
            connection_information: the connection information to use for transmitting messages
            protocol_map: a protocol map for converting messages to bytes
            close_callback: the call back to call to close the current connection
        """
        self.logger = logger
        self.sock = connection_information.sock
        self.addr = connection_information.addr
        self.buffer = b""
        self.protocol_map = protocol_map
        self.close_callback = close_callback
    
    def write(self):
        """Writes bytes in the buffer to the connection socket"""
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
        """Starts transmitting the message with specified type code and values to the connection peer"""
        message = self.protocol_map.pack_values_given_type_code(type_code, *values)
        self.buffer += message
        self.write()

class Message:
    """Class for keeping track of type the code and message values for a message"""
    def __init__(self, type_code, values):
        self.type_code = type_code
        self.values = values

    def __str__(self):
        return f"Type Code: {self.type_code}, Values: {self.values}"

class MessageReceiver:
    def __init__(self, logger, connection_information: ConnectionInformation, message_handler: protocol.MessageHandler, close_callback):
        """
            Converts messages received over a connection into Message objects
            logger: a logger object for logging errors and significant occurrences
            connection_information: information on the connection used to receive bytes
            message_handler: a message handler object for converting bytes to messages
            close_callback: a callback function to use to close the current connection
        """
        self.logger = logger
        self.sock = connection_information.sock
        self.addr = connection_information.addr
        self.message_handler: protocol.MessageHandler = message_handler
        self.buffer = b""
        self.messages = []
        self.close_callback = close_callback

    def _read(self):
        """Puts data from the socket into the buffer"""
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
        """Processes newly received bytes"""
        self._read()
        self.process_message()
    
    def process_complete_message(self):
        """Finishes handling a completed message"""
        values = self.message_handler.get_values()
        type_code = self.message_handler.get_protocol_type_code()
        content_length = self.message_handler.get_number_of_bytes_extracted()
        self.message_handler.prepare_for_next_message()
        message = Message(type_code, values)
        self.messages.append(message)
        print("received message with type code", type_code, repr(message), "from", self.addr)
        if len(self.buffer) > 0:
            #If there is anything still in the buffer, process the new request
            #This is necessary because the selector will only call read when bytes are received, which will cause issues if multiple messages arrive simultaneously
            self.buffer = self.buffer[content_length:]
            self.process_message()

    def process_message(self):
        """Converts bytes into messages"""
        self.message_handler.receive_bytes(self.buffer)
        if self.message_handler.is_done_obtaining_values():
            self.process_complete_message()
        else:
            self.buffer = b""

    def has_processed_messages(self):
        """Returns true if the bytes have been converted into at least one complete message"""
        return len(self.messages) > 0

    def extract_message(self) -> Message:
        """Extracts the next complete message. Messages are extracted in the order in which they are received."""
        message = self.messages.pop(0)
        return message

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
        self.logger = logger
        self.message_sender = MessageSender(self.logger, self.connection_information, sending_protocol_map, self.close)
        self.callback_handler = callback_handler
        message_handler = protocol.MessageHandler(receiving_protocol_map)
        self.message_receiver = MessageReceiver(self.logger, connection_information, message_handler, self.close)

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
        self.selector.modify(self.connection_information.sock, events, data=self)

    def send_response_to_request(self, request: Message):
        message_values = self.callback_handler.pass_values_to_protocol_callback(request.values, request.type_code)
        if self.is_server:
            response = Message(request.type_code, message_values)
            self.send_message(response)

    def respond_to_request(self):
        request = self.message_receiver.extract_message()
        if self.callback_handler.has_protocol(request.type_code):
            self.send_response_to_request(request)
        elif not self.is_server:
            print(f"Received message with type code {request.type_code}! values: {request.values}")
        
    def read(self):
        self.message_receiver.read()
        while self.message_receiver.has_processed_messages():
            self.respond_to_request()

    def send_message(self, request: Message):
        print(f"Sending message {request}")
        self.message_sender.send_message(request.type_code, request.values)

    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.message_sender.write()
    
    def close(self):
        self.logger.log_message(f"closing connection to {self.connection_information.addr}")
        try:
            self.selector.unregister(self.connection_information.sock)
        except Exception as e:
            self.logger.log_message(f"error: selector.unregister() exception for {self.connection_information.addr}: {repr(e)}")
        try:
            self.connection_information.sock.close()
        except OSError as e:
            self.logger.log_message(f"error: socket.close() exception for {self.connection_information.addr}: {repr(e)}")
        finally:
            # Delete reference to socket object for garbage collection
            self.connection_information.sock = None
        
    