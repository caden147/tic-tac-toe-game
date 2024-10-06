
import sys
import selectors
import io
import struct

from source import protocol, protocol_definitions


class Message:
    def __init__(self, selector, sock, addr, request):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self.request = request
        self._recv_buffer = b""
        self._send_buffer = b""
        self._request_queued = False
        self.response = None

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
            print("sending", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]

    def _create_message(
        self, *, type_code, content_bytes
    ):
        message = protocol_definitions.SERVER_PROTOCOL_MAP.pack_values_given_type_code(type_code, content_bytes)
        return message

    def _process_response_binary_content(self):
        content = self.response
        print(f"got response: {repr(content)}")

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
        if not self._request_queued:
            self.queue_request()

        self._write()

        if self._request_queued:
            if not self._send_buffer:
                # Set selector to listen for read events, we're done writing.
                self._set_selector_events_mask("r")

    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                f"error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                f"error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None

    def queue_request(self):
        content = self.request["content"]
        content_type = self.request["type"]
        content_encoding = self.request["encoding"]
        req = {
                "content_bytes": content,
                "content_type": content_type,
                "content_encoding": content_encoding,
            }
        message = self._create_message(**req)
        self._send_buffer += message
        self._request_queued = True

    def process_response_type_code(self):
        if len(self._recv_buffer) >= protocol.TYPE_CODE_SIZE:
            self.request_type_code = protocol.unpack_type_code_from_message(self._recv_buffer)
            self._recv_buffer = protocol.compute_message_after_type_code(self.request_type_code)
            self.message_handler.update_protocol(self.request_type_code)

    def process_response(self):
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
            print("received request with type code", self.response_type_code, repr(self.request), "from", self.addr)
            # Set selector to listen for write events, we're done reading.
            self._set_selector_events_mask("w")
        # Close when response has been processed
        self.close()
