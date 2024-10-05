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
        field_length = struct.pack(">H", 20)
        protocol = self._create_protocol()
        unpacked_field_length = protocol.unpack_field_length(0, field_length, 0)
        self.assertEqual(unpacked_field_length, 20)

    def test_correctly_unpacks_text(self):
        text = "This is a test"
        encoded_text = text.encode("utf-8")
        packed_text = struct.pack(">" + str(len(encoded_text)) + "s", encoded_text)
        protocol = self._create_protocol()
        unpacked_text = protocol.unpack_variable_length_field(0, len(encoded_text), packed_text, 0)
        self.assertEqual(unpacked_text, text)
    
    def test_gives_correct_field_information(self):
        protocol = self._create_protocol()
        expected_field_name = "text"
        expected_max_size = 2
        self.assertTrue(protocol.is_last_field(0))
        self.assertEqual(protocol.compute_variable_length_field_max_size(0), expected_max_size)
        self.assertEqual(protocol.compute_field_name(0), expected_field_name)

    def test_correctly_packs_text(self):
        protocol = self._create_protocol()
        text = "testing"
        encoded_text = text.encode("utf-8")
        text_length = len(encoded_text)
        expected = struct.pack(">BH" + str(text_length) + "s", 0, text_length, encoded_text)
        packed_text = protocol.pack(text)
        self.assertEqual(expected, packed_text)

class TestSingleFieldFixedLengthProtocol(unittest.TestCase):
    def _create_protocol(self):
        return protocol.create_single_byte_positive_integer_message_protocol(12)
    
    def test_computes_correct_field_string(self):
        expected = ">B"
        actual = self._create_protocol().compute_fields_string()
        self.assertEqual(expected, actual)
    
    def test_can_correctly_pack_argument(self):
        value = 10
        protocol = self._create_protocol()
        actual = protocol.pack(value)
        expected = struct.pack(">BB", 12, 10)
        self.assertEqual(actual, expected)

    def test_returns_correct_type_code(self):
        expected = 12
        actual = self._create_protocol().get_type_code()
        self.assertEqual(expected, actual)

    def test_can_correctly_unpack_message(self):
        protocol = self._create_protocol()
        input_bytes = struct.pack(">B", 100)
        expected_result = {'number': 100}
        actual_result = protocol.unpack(input_bytes)
        self.assertEqual(expected_result, actual_result)

    def test_returns_correct_size(self):
        protocol = self._create_protocol()
        expected = 1
        actual = protocol.get_size()
        self.assertEqual(actual, expected)

    def test_returns_correct_number_of_fields(self):
        protocol = self._create_protocol()
        expected = 1
        actual = protocol.get_number_of_fields()
        self.assertEqual(actual, expected)

def encode_text(text):
    return text.encode("utf-8")

def decode_text(input_bytes):
    return input_bytes.decode(utf-8)

class TestComplexVariableLengthMessageProtocol(unittest.TestCase):
    def _create_protocol(self):
        first_field = protocol.create_string_protocol_field('name', 2)
        second_field = protocol.create_string_protocol_field('password', 1)
        third_field = protocol.create_single_byte_positive_integer_protocol_field('type')
        result = protocol.VariableLengthMessageProtocol(2, [first_field, second_field, third_field])
        return result

    def test_can_correctly_pack_values(self):
        name = 'bob versus chuck'
        password = '1'*100    
        game_type = 30
        protocol = self._create_protocol()
        actual = protocol.pack(name, password, game_type)
        encoded_name = encode_text(name)
        encoded_password = encode_text(password)
        expected = struct.pack(">BH16sB100sB", 2, 16, encoded_name, 100, encoded_password, game_type)
        self.assertEqual(expected, actual)


if __name__ == '__main__':
    unittest.main()