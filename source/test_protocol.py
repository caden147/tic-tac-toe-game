import unittest
import protocol
import struct

class TestMessageProtocol(unittest.TestCase):
    def _create_protocol(self):
        return protocol.create_text_message_protocol(0)

    def test_protocol_returns_correct_type_code(self):
        protocol = self._create_protocol()
        self.assertEqual(protocol.get_type_code(), 0)

    def test_protocol_is_not_fixed_length(self):
        protocol = self._create_protocol()
        self.assertFalse(protocol.is_fixed_length())

    def test_correctly_unpacks_field_length(self):
        field_length = struct.pack(">I", 20)
        protocol = self._create_protocol()
        unpacked_field_length = protocol.unpack_field_length(0, field_length, 0)
        self.assertEqual(unpacked_field_length, 20)

    def test_correctly_unpacks_text(self):
        text = "This is a test"
        encoded_text = text.encode("utf-8")
        packed_text = struct.pack(">" + str(len(encoded_text)) + "s", encoded_text)
        protocol = self._create_protocol()
        unpacked_text = protocol.unpack_variable_length_field(0, len(encoded_text), packed_text, 0).decode("utf-8")
        self.assertEqual(unpacked_text, text)

if __name__ == '__main__':
    unittest.main()