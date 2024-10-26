import connection_handler

class MockInternet:
    def __init__(self):
        """Used by socket simulating classes to send information to each other"""
        self.sockets = {}

    def register_socket(self, address, socket):
        self.sockets[address] = socket

    def message_socket(self, address, message):
        target = self.sockets[address]
        target.receive_message_from_socket(message)

    def get_socket(self, address):
        return self.sockets[address]

    def connect_to_listening_socket(self, target_address, source_address):
        listening_socket = self.get_socket(target_address)
        return listening_socket.create_response_socket(source_address)

    def transmit_connection_closing(self, address):
        target = self.sockets[address]
        target.close()

class MockTCPSocket:
    SENDING_LIMIT = 1500
    def __init__(self, internet: MockInternet, address):
        """Simulates a TCP socket for testing purposes"""
        self.internet = internet
        self.address = address
        self.receive_buffer = b""
        self.open_for_reading = False
        self.open_for_writing = False
        self.has_closed = False
        self.peer = None
    
    def send(self, message_bytes):
        """Simulates sending the following bytes and returns the number of bytes sent"""
        bytes_to_send = message_bytes[:self.SENDING_LIMIT]
        self.internet.message_socket(self.peer.get_address(), bytes_to_send)
        return len(bytes_to_send)

    def recv(self, amount_of_bytes_to_receive: int):
        """Retrieves at most the amount of bytes to receive from the buffer. Returns None if the peer closes"""
        if self.has_closed():
            return None
        else:
            result = self.receive_buffer[:amount_of_bytes_to_receive]
            self.receive_buffer = self.receive_buffer[amount_of_bytes_to_receive:]
            return result
            

    def close(self):
        """Closes the connection"""
        self.open_for_reading = False
        self.open_for_writing = False
        self.has_closed = True

    def connect_ex(self, address):
        """Connects to the specified address"""
        self.peer = self.internet.connect_to_listening_socket(address, self.address)

    def set_peer(self, peer):
        self.peer = peer

    def setblocking(self, value):
        pass

    def receive_message_from_socket(self, message, address):
        self.receive_buffer += message

    def get_address(self):
        return self.address

    def get_peer_address(self):
        return self.peer.get_address()

    def has_received_bytes(self):
        return len(self.receive_buffer) > 0


class MockListeningSocket:
    def __init__(self, internet: MockInternet, address):
        """Simulates a listening socket that creates connections"""
        self.internet = internet
        self.address = address
        self.last_port_used = self.address[1]
        self.is_listening = False
        self.created_sockets = []

    def setsockopt(self, *args):
        pass

    def bind(self, address):
        self.address = address

    def listen(self):
        self.is_listening = True

    def setblocking(self, value):
        pass

    def create_response_socket(self, address):
        self.last_port_used += 1
        host = self.address[0]
        new_socket = MockTCPSocket(self.internet, (host, self.last_port_used))
        peer = self.internet.get_socket(address)
        new_socket.set_peer(peer)
        self.created_sockets.append(new_socket)

    def accept(self):
        next_socket = self.created_sockets.pop()
        return next_socket, next_socket.get_peer_address()

class MockKey:
    def __init__(self, data, address, socket=None):
        self.data = data
        self.fileobj = socket
        self.address = address

    #The equality method and hash method must be implemented to use this as a dictionary key
    def __eq__(self, other) -> bool:
        return isinstance(other, MockKey) and self.address == other.address

    def __hash__(self):
        return hash(self.address)

class MockSelector:
    def __init__(self):
        self.sockets = {}

    def select(self, timeout=None):
        pass

    def register(self, socket, flags, data: connection_handler.ConnectionHandler):
        key = MockKey(data, socket)
        data._set_selector_events_mask(flags)
        self.sockets[key] = data

    def unregister(self, socket):
        for key in self.sockets:
            if key.fileobj == socket:
                self.sockets.pop(key)
                return 
