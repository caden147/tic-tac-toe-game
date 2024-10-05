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

    def _create_packed_example(self):
        name = 'bob versus chuck'
        password = '1'*100    
        game_type = 30
        encoded_name = encode_text(name)
        encoded_password = encode_text(password)
        packing = struct.pack(">BH16sB100sB", 2, 16, encoded_name, 100, encoded_password, game_type)
        values = {'name': name, 'password': password, 'type': game_type}
        return packing, values

    def test_can_correctly_pack_values(self):
        protocol = self._create_protocol()
        expected, values = self._create_packed_example()
        actual = protocol.pack(values['name'], values['password'], values['type'])
        self.assertEqual(expected, actual)

    def test_can_correctly_unpack_values(self):
        message_protocol = self._create_protocol()
        protocol_map = protocol.ProtocolMap([message_protocol])
        message_handler = protocol.MessageHandler(protocol_map)
        packing, expected = self._create_packed_example()
        packing = packing[1:]
        message_handler.update_protocol(2)
        message_handler.receive_bytes(packing)
        values = message_handler.get_values()
        self.assertEqual(len(expected), len(values))
        for key in expected:
            self.assertEqual(expected[key], values[key])
        self.assertTrue(message_handler.is_done_obtaining_values())

class TestMultipleFieldFixedLengthMessageProtocol(unittest.TestCase):
    def _compute_protocol(self):
        first_field = protocol.create_single_byte_positive_integer_protocol_field('1')
        second_field = protocol.create_single_byte_positive_integer_protocol_field('2')
        result = protocol.FixedLengthMessageProtocol(100, [first_field, second_field])
        return result

    def test_has_correct_size(self):
        expected = 2
        actual = self._compute_protocol().get_size()
        self.assertEqual(expected, actual)

    def test_has_correct_number_of_fields(self):
        expected = 2
        actual = self._compute_protocol().get_number_of_fields()
        self.assertEqual(expected, actual)

    def _create_pack_and_values(self):
        first_value = 90
        second_value = 0
        values = {"1": first_value, "2": second_value}
        packing = struct.pack(">BBB", 100, first_value, second_value)
        return packing, values

    def test_can_pack_values_correctly(self):
        message_protocol = self._compute_protocol()
        expected, values = self._create_pack_and_values()
        actual = message_protocol.pack(values["1"], values["2"])
        self.assertEqual(expected, actual)

    def test_can_unpack_values_correctly(self):
        message_protocol = self._compute_protocol()
        pack, expected = self._create_pack_and_values()
        pack = pack[1:]
        actual = message_protocol.unpack(pack)
        self.assertEqual(expected, actual)

def create_values_dictionary(values, names):
    result = {}
    for i in range(len(values)):
        result[names[i]] = values[i]
    return result

class TestMessageHandler(unittest.TestCase):
    def _create_protocol_map(self):
        message_protocol = protocol.create_text_message_protocol(0)
        nonnegative_integer_protocol = protocol.create_single_byte_positive_integer_message_protocol(1)
        protocol_map = protocol.ProtocolMap([message_protocol, nonnegative_integer_protocol])
        return protocol_map
    
    def _create_values_and_names(self):
        return [['message'], [1]], [['text'], ['number']]

    def test_handles_full_values(self):
        protocol_map = self._create_protocol_map()
        values, names = self._create_values_and_names()
        message_handler = protocol.MessageHandler(protocol_map)
        for i in range(1):
            packing = protocol_map.pack_values_given_type_code(i, *values[i])
            type_code = protocol.unpack_type_code_from_message(packing)
            packing = protocol.compute_message_after_type_code(packing)
            message_handler.update_protocol(type_code)
            message_handler.receive_bytes(packing)
            self.assertTrue(message_handler.is_done_obtaining_values())
            expected = create_values_dictionary(values[i], names[i])
            actual = message_handler.get_values()
            self.assertEqual(expected, actual)



if __name__ == '__main__':
    unittest.main()