class MockInternet:
    def __init__(self):
        """Used by socket simulating classes to send information to each other"""
        self.sockets = {}

    def register_socket(self, address, socket):
        self.sockets[address] = socket

    def message_socket(self, address, message):
        target = self.sockets[address]
        target.receive_message_from_socket(message)

class MockTCPSocket:
    def __init__(self, internet: MockInternet):
        """Simulates a TCP socket for testing purposes"""
        self.internet = internet
        self.address = None
        self.receive_buffer
        self.open_for_reading = False
        self.open_for_writing = False
        self.has_closed = False
        self.peer = None
    
    def send(self, message_bytes):
        """Simulates sending the following bytes and returns the number of bytes sent"""
        self.internet.message_socket(self.peer.get_address(), message_bytes)

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
        pass

    def setblocking(self, value):
        pass

    def receive_message_from_socket(self, message, address):
        self.receive_buffer += message

    def get_address(self):
        return self.address


class MockListeningSocket:
    def __init__(self):
        """Simulates a listening socket that creates connections"""
        self.address
        self.is_listening = False

    def setsockopt(self, *args):
        pass

    def bind(self, address):
        self.address = address

    def listen(self):
        self.is_listening = True

    def setblocking(self, value):
        pass