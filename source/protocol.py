import struct

TYPE_CODE_SIZE = 1
def pack_type_code(type_code: int):
    return struct.pack(">B", type_code)

def unpack_type_code_from_message(message):
    relevant_bytes = message[:TYPE_CODE_SIZE]
    type_code = struct.unpack(">B", relevant_bytes)[0]
    return type_code

def compute_message_after_type_code(message):
    return message[TYPE_CODE_SIZE:]

def compute_format_representation_for_size(size: int):
    """
        Computes the appropriate format string representation for the size of a field
        size: the desired size in number of bytes
    """
    if size == 1:
        return 'B'
    elif size == 2:
        return 'H'
    elif size == 4:
        return 'I'
    elif size == 8:
        return 'L'
    else:
        raise ValueError("Tried to create byte format string text for invalid size")

def encode_value(value):
    if type(value) == str:
        return value.encode("utf-8")
    return value

def decode_value(value):
    if type(value) == bytes:
        return value.decode("utf-8")
    return value

class ByteStream:
    def __init__(self, input_bytes):
        self.bytes = bytearray(input_bytes)
        self.index = 0
    
    def append(self, input_bytes):
        self.bytes.extend(input_bytes)

    def extract(self, amount: int):
        ending = self.index + amount
        result = self.bytes[self.index:ending]    
        self.index = ending
        return result

    def size(self):
        return len(self.bytes) - self.index


class ProtocolField:
    def get_name(self):
        pass
    
    def compute_struct_text(self):
        """Gives the text used to represent the field in a struct.pack or struct.unpack call"""
        pass

    def is_fixed_length(self):
        return True

class ConstantLengthProtocolField(ProtocolField):
    def __init__(self, name: str, struct_text: str, size: int):
        self.name = name
        self.struct_text = struct_text
        self.size = size

    def get_name(self):
        return self.name
    
    def compute_struct_text(self):
        return self.struct_text
    
    def get_size(self):
        return self.size
    
class VariableLengthProtocolField(ProtocolField):
    def __init__(self, name: str, create_struct_text, max_size: int = 1):
        self.name = name
        self.create_struct_text = create_struct_text
        self.max_size = max_size
    
    def get_name(self):
        return self.name
    
    def compute_struct_text(self, size):
        return self.create_struct_text(size)
    
    def compute_struct_text_from_value(self, value):
        return self.compute_struct_text(len(value))

    def get_max_size(self):
        return self.max_size
    
    def is_fixed_length(self):
        return False

def create_string_protocol_field(name, max_size_in_bytes):
    def create_struct_text(size):
        return str(size) + "s"
    field = VariableLengthProtocolField(name, create_struct_text, max_size_in_bytes)
    return field

def create_single_byte_positive_integer_protocol_field(name):
    field = ConstantLengthProtocolField(name, "B", 1)
    return field

class MessageProtocol:
    def get_type_code(self):
        pass

    def pack(self, *args):
        pass

    def is_fixed_length(self):
        return True
    
    def get_number_of_fields(self):
        pass

class TypeCodeOnlyMessageProtocol(MessageProtocol):
    def __init__(self, type_code):
        self.type_code = type_code
    
    def get_type_code(self):
        return self.type_code

    def get_number_of_fields(self):
        return 0

    def pack(self, *args):
        return pack_type_code(self.type_code)

class FixedLengthMessageProtocol(MessageProtocol):
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields
        self.size = self._compute_size()

    def compute_fields_string(self):
        text = ">"
        for field in self.fields:
            text += field.compute_struct_text()
        return text

    def pack(self, *args):
        args = [encode_value(value) for value in args]
        type_code_bytes = pack_type_code(self.type_code)
        values_bytes = struct.pack(self.compute_fields_string(), *args)
        return type_code_bytes + values_bytes

    def unpack(self, input_bytes):
        results = {}
        values = struct.unpack(self.compute_fields_string(), input_bytes)
        for i in range(len(values)):
            name = self.fields[i].get_name()
            results[name] = decode_value(values[i])
        return results

    def get_type_code(self):
        return self.type_code
    
    def _compute_size(self):
        """Returns the size in bytes of a message using the protocol"""
        size = 0
        for i in range(len(self.fields)):
            size += self.fields[i].get_size()
        return size
    
    def get_size(self):
        return self.size

    def get_number_of_fields(self):
        return len(self.fields)

def create_fieldless_message_protocol(type_code):
    return TypeCodeOnlyMessageProtocol(type_code)

class VariableLengthMessageProtocol(MessageProtocol):
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields
    
    def get_type_code(self):
        return self.type_code

    def is_fixed_length(self):
        return False
    
    def pack(self, *args):
        args = [encode_value(value) for value in args]
        values_bytes = pack_type_code(self.type_code)
        for index, field in enumerate(self.fields):
            if field.is_fixed_length():
                field_bytes = struct.pack(">" + field.compute_struct_text(), args[index])
            else:
                field_bytes = struct.pack(">" + field.compute_struct_text_from_value(args[index]), args[index])
                size = len(field_bytes)
                size_bytes = struct.pack(">" + compute_format_representation_for_size(field.get_max_size()), size)
                field_bytes = size_bytes + field_bytes
            values_bytes += field_bytes
        return values_bytes
    
    def is_field_fixed_length(self, i):
        return self.fields[i].is_fixed_length()

    def is_last_field(self, i):
        return i == len(self.fields) - 1
    
    def compute_fixed_length_field_length(self, i):
        field = self.fields[i]
        return field.get_size()
    
    def compute_variable_length_field_max_size(self, i):
        field = self.fields[i]
        return field.get_max_size()
        
    def unpack_field_length(self, i, input_bytes, starting_index):
        maximum_size = self.compute_variable_length_field_max_size(i)
        relevant_bytes = input_bytes[starting_index: starting_index + maximum_size]
        return struct.unpack(">" + compute_format_representation_for_size(maximum_size), relevant_bytes)[0]

    def unpack_variable_length_field(self, i, length, input_bytes, starting_index):
        field = self.fields[i]
        relevant_bytes = input_bytes[starting_index: starting_index + length]
        return decode_value(struct.unpack(">" + field.compute_struct_text(length), relevant_bytes)[0])
    
    def unpack_fixed_length_field(self, i, input_bytes, starting_index):
        field = self.fields[i]
        length = self.compute_fixed_length_field_length(i)
        relevant_bytes = input_bytes[starting_index: starting_index + length]
        return decode_value(struct.unpack(">" + field.compute_struct_text(), relevant_bytes)[0])
    
    def compute_field_name(self, i):
        field = self.fields[i]
        return field.get_name()
    
    def get_number_of_fields(self):
        return len(self.fields)

class ProtocolMap:
    """Maps between type codes and protocols"""
    def __init__(self, protocols):
        """protocols: an iterable of MessageProtocols"""
        self.map = {}
        for protocol in protocols:
            self.map[protocol.get_type_code()] = protocol
        
    def get_protocol_with_type_code(self, code: int):
        """Returns the protocol with the associated type code"""
        return self.map[code]
    
    def has_protocol_with_type_code(self, code: int):
        """Returns true if the map has a protocol with the specified type code and false otherwise"""
        return code in self.map

    def pack_values_given_type_code(self, code: int, *values):
        message_protocol = self.get_protocol_with_type_code(code)
        result = message_protocol.pack(*values)
        return result
    
class MessageHandler:
    """
        A message handler object is used to parse bytes being sent as part of a message utilizing a protocol map.
        This handles when are not all sent at the same time.
        protocol_map: a protocol map object containing message protocols that the handler should handle.
        How to use:
            Upon receiving a message, you must parse the type code using something other than the message handler
            and then pass it to the handler using the update_protocol method with the protocol code.
            Pass bytes after the type code to the message handler using the receive_bytes method.
            Figure out if the handler is done parsing the message or needs more bites using the is_done_obtaining_values method.
            Get the parse values as a dictionary using the get_values method.
            Get the number of bytes that were extracted as part of the message using the get_number_of_bytes_extracted method.
    """
    def __init__(self, protocol_map: ProtocolMap):
        self.protocol_map = protocol_map
        self._initialize()
    
    def _initialize(self, protocol = None):
        self.bytes = None
        self.protocol: MessageProtocol = protocol
        self.values = {}
        self.field_index = -1
        self.bytes_index = 0
        self.next_expected_size = None
        self.is_done = False

    def _update_bytes(self, input_bytes):
        if self.bytes:
            self.bytes += input_bytes
        else:
            self.bytes = input_bytes

    def _update_values_based_on_fixed_length_protocol(self):
        if len(self.bytes) >= self.protocol.get_size():
            self.values = self.protocol.unpack(self.bytes)
            self.is_done = True

    def _update_next_expected_size(self):
        if self.protocol.is_field_fixed_length(self.field_index):
            self.next_expected_size = self.protocol.compute_fixed_length_field_length(self.field_index)
        else:
            self.next_expected_size = None

    def _advance_field(self):
        if self.field_index >= 0 and self.field_index < self.protocol.get_number_of_fields():
            if self.protocol.is_field_fixed_length(self.field_index):
                name = self.protocol.compute_field_name(self.field_index)
                value = self.protocol.unpack_fixed_length_field(
                    self.field_index,
                    self.bytes,
                    self.bytes_index
                )
            else:
                name = self.protocol.compute_field_name(self.field_index)
                value = self.protocol.unpack_variable_length_field(
                    self.field_index,
                    self.next_expected_size,
                    self.bytes,
                    self.bytes_index
                )
                
            self.values[name] = value
            self.bytes_index += self.next_expected_size
        self.field_index += 1
        if self.field_index >= self.protocol.get_number_of_fields():
            self.is_done = True
        else:
            self._update_next_expected_size()
            self._update_values_based_on_variable_length_protocol()

    def _update_values_based_on_variable_length_protocol(self):
        if self.field_index < 0:
            self._advance_field()
        number_of_new_bytes = len(self.bytes) - self.bytes_index
        if self.next_expected_size:
            if number_of_new_bytes >= self.next_expected_size:
                self._advance_field()
        elif number_of_new_bytes >= self.protocol.compute_variable_length_field_max_size(self.field_index):
            self.next_expected_size = self.protocol.unpack_field_length(
                self.field_index,
                self.bytes,
                self.bytes_index
            )
            self.bytes_index += self.protocol.compute_variable_length_field_max_size(self.field_index)
            self._update_values_based_on_variable_length_protocol()

    def _update_values(self):
        if self.protocol.is_fixed_length():
            self._update_values_based_on_fixed_length_protocol()
        else:
            self._update_values_based_on_variable_length_protocol()

    def receive_bytes(self, input_bytes):
        self._update_bytes(input_bytes)
        self._update_values()

    def update_protocol(self, type_code):
        protocol = self.protocol_map.get_protocol_with_type_code(type_code)
        self._initialize(protocol)

    def is_done_obtaining_values(self):
        return self.is_done

    def get_values(self):
        return self.values
    
    def get_number_of_bytes_extracted(self):
        return self.bytes_index

class ProtocolCallbackHandler:
    def __init__(self):
        self.callbacks = {}
    
    def register_callback_with_protocol(self, callback, protocol_type_code):
        self.callbacks[protocol_type_code] = callback
    
    def pass_values_to_protocol_callback_with_connection_information(self, values, protocol_type_code, connection_information):
        return self.callbacks[protocol_type_code](values, connection_information)

    def pass_values_to_protocol_callback(self, values, protocol_type_code):
        return self.callbacks[protocol_type_code](values)

    def has_protocol(self, protocol_type_code):
        return protocol_type_code in self.callbacks

def is_any_field_variable_length(fields):
    for field in fields:
        if not field.is_fixed_length():
            return True
    return False

def create_protocol_with_fields(type_code: int, fields = None):
    if isinstance(fields, ProtocolField):
        fields = [fields]
    if is_any_field_variable_length(fields):
        protocol = VariableLengthMessageProtocol(type_code, fields)
    else:
        protocol = FixedLengthMessageProtocol(type_code, fields)
    return protocol

def create_protocol(type_code: int, fields = None):
    """
        Creates a MessageProtocol object using a type code and optional fields. 
        type_code: an integer number used to distinguish between different message protocols. 
        Every MessageProtocol objects should have a unique type code.
        The type code is sent with every message conforming to the protocol.
        fields: an optional list of fields or a single field. 
        Every field object defines the type of value that should go in the field
        as well as the number of bytes the field can have. 
    """
    protocol = None
    if not fields:
        protocol = create_fieldless_message_protocol(type_code)
    else:
        protocol = create_protocol_with_fields(type_code, fields)
    return protocol

def create_text_message_protocol(type_code: int):
    field = create_string_protocol_field("text", 2)
    protocol = create_protocol(type_code, field)
    return protocol

def create_single_byte_positive_integer_message_protocol(type_code: int):
    field = create_single_byte_positive_integer_protocol_field('number')
    protocol = create_protocol(type_code, field)
    return protocol