class MockTCPSocket:
    def __init__(self):
        """Simulates a TCP socket for testing purposes"""
        self.address = None
        self.receive_buffer
        self.open_for_reading = False
        self.open_for_writing = False
        self.has_closed = False
        self.peer = None
    
    def send(self, bytes):
        """Simulates sending the following bytes and returns the number of bytes sent"""
        pass

    def recv(self, amount_of_bytes_to_receive: int):
        """Retrieves at most the amount of bytes to receive from the buffer. Returns None if the peer closes"""
        pass

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