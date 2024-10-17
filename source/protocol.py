import struct
from protocol_fields import *
from protocol_type_codes import *

def compute_format_representation_for_size(size: int):
    """
        Computes the appropriate format string representation for the size of a field
        size: the desired size in number of bytes
        Currently only sizes 1, 2, 4 and 8 are supported.
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
        raise ValueError("Tried to create byte format string text for invalid size! Must be 1, 2, 4, or 8!")

def encode_value(value):
    """
        Encodes a value into an appropriate byte format for packing it
        value: a value to be packed into bytes
    """
    if type(value) == str:
        return value.encode("utf-8")
    return value

def decode_value(value):
    """
        Decodes a value unpacked if it is still in byte format
        value: an unpacked value that might still be in byte format and need to be decoded
    """
    if type(value) == bytes:
        return value.decode("utf-8")
    return value

class MessageProtocol:
    """
        Interface class for the MessageProtocol objects.
        A message protocol object defines how to convert between values associated with a message for the protocol
        and messages conforming to the protocol
    """
    def get_type_code(self):
        """Returns a type code integer defining which protocol it is"""
        pass

    def pack(self, *args):
        """Packs values into a message conforming to the protocol"""
        pass

    def is_fixed_length(self):
        """Returns true if the protocol is for fixed length messages and false otherwise"""
        return True
    
    def get_number_of_fields(self):
        """Returns the number of fields supported by the protocol"""
        pass

class TypeCodeOnlyMessageProtocol(MessageProtocol):
    """
        Defines a message protocol that only consists of a type code and no fields
        type_code: the type code for the protocol
    """
    def __init__(self, type_code):
        self.type_code = type_code
    
    def get_type_code(self):
        """Returns a type code integer defining which protocol it is"""
        return self.type_code

    def get_number_of_fields(self):
        """Returns the number of fields associated with the message protocol, in this case 0"""
        return 0

    def pack(self, *args):
        """Returns a message for the protocol containing only the type code"""
        return pack_type_code(self.type_code)

class FixedLengthMessageProtocol(MessageProtocol):
    """
        Defines a fixed length message protocol
        type_code: the type code for the protocol
        fields: the fields corresponding to the protocol
    """
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields
        self.size = self._compute_size()

    def compute_fields_string(self):
        """Returns a string for packing and unpacking messages conforming to the protocol"""
        text = ">"
        for field in self.fields:
            text += field.compute_struct_text()
        return text

    def pack(self, *args):
        """Pacs values into a message conforming to the protocol"""
        args = [encode_value(value) for value in args]
        type_code_bytes = pack_type_code(self.type_code)
        values_bytes = struct.pack(self.compute_fields_string(), *args)
        return type_code_bytes + values_bytes

    def unpack(self, input_bytes):
        """
            Unpacks bytes corresponding to the protocol excluding the type code at the beginning into the contained values
            input_bytes: bytes for a message corresponding to the protocol excluding the type code
            returns: a dictionary mapping field names to the corresponding values
        """
        results = {}
        values = struct.unpack(self.compute_fields_string(), input_bytes)
        for i in range(len(values)):
            name = self.fields[i].get_name()
            results[name] = decode_value(values[i])
        return results

    def get_type_code(self):
        """Returns the type code associated with the protocol"""
        return self.type_code
    
    def _compute_size(self):
        """Returns the size in bytes of a message using the protocol"""
        size = 0
        for i in range(len(self.fields)):
            size += self.fields[i].get_size()
        return size
    
    def get_size(self):
        """Returns the size in bytes of a message using the protocol"""
        return self.size

    def get_number_of_fields(self):
        """Returns the number of fields corresponding to the protocol"""
        return len(self.fields)

def create_fieldless_message_protocol(type_code):
    """Creates a field less message protocol using the type code"""
    return TypeCodeOnlyMessageProtocol(type_code)

class VariableLengthMessageProtocol(MessageProtocol):
    """
        Defines a variable length message protocol
        type_code: the type code for the protocol
        fields: the fields corresponding to the protocol
    """
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields
    
    def get_type_code(self):
        """Returns the type code for the message protocol"""
        return self.type_code

    def is_fixed_length(self):
        """Returns false to indicate that this is not a fixed length message protocol"""
        return False
    
    def pack(self, *args):
        """Pacs values into a message conforming to the protocol"""
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
        """Returns true if the field at index i is fixed length and false otherwise"""
        return self.fields[i].is_fixed_length()

    def is_last_field(self, i):
        """Returns true if the field at index i is the last and false otherwise"""
        return i == len(self.fields) - 1
    
    def compute_fixed_length_field_length(self, i):
        """Returns the field length for the field at index i assuming that it is fixed length"""
        field = self.fields[i]
        return field.get_size()
    
    def compute_variable_length_field_max_size(self, i):
        """Returns the maximum field length for the field at index i assuming that it is variable length"""
        field = self.fields[i]
        return field.get_max_size()
        
    def unpack_field_length(self, i, input_bytes, starting_index):
        """
            Unpacks a field length into an integer value
            i: the index of the corresponding field
            input_bytes: part of a message in bytes corresponding to the protocol
            starting_index: the start of the bytes in the message containing the field length
        """
        maximum_size = self.compute_variable_length_field_max_size(i)
        relevant_bytes = input_bytes[starting_index: starting_index + maximum_size]
        return struct.unpack(">" + compute_format_representation_for_size(maximum_size), relevant_bytes)[0]

    def unpack_variable_length_field(self, i, length, input_bytes, starting_index):
        """
            Unpacks a variable length field value
            i: the index for the field
            length: the length of the field value
            input_bytes: part of a message in bytes corresponding to the protocol
            starting_index: the start of the bytes in the message containing the value
        """
        field = self.fields[i]
        relevant_bytes = input_bytes[starting_index: starting_index + length]
        return decode_value(struct.unpack(">" + field.compute_struct_text(length), relevant_bytes)[0])
    
    def unpack_fixed_length_field(self, i, input_bytes, starting_index):
        """
            Unpacks bytes corresponding to a fixed length field
            i: the index for the field
            input_bytes: part of a message in bytes corresponding to the protocol
            starting_index: the start of the bytes in the message containing the value
        """
        field = self.fields[i]
        length = self.compute_fixed_length_field_length(i)
        relevant_bytes = input_bytes[starting_index: starting_index + length]
        return decode_value(struct.unpack(">" + field.compute_struct_text(), relevant_bytes)[0])
    
    def compute_field_name(self, i):
        """Returns the name of the field at the specified index"""
        field = self.fields[i]
        return field.get_name()
    
    def get_number_of_fields(self):
        """Returns the number of fields corresponding to the protocol"""
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
        """
            Packs values for a message protocol into bytes
            code: the type code for the protocol
            values: the values to pack
        """
        message_protocol = self.get_protocol_with_type_code(code)
        result = message_protocol.pack(*values)
        return result
    
class MessageHandler:
    """
        A message handler object is used to parse bytes being sent as part of a message utilizing a protocol map.
        This handles when are not all sent at the same time.
        protocol_map: a protocol map object containing message protocols that the handler should handle.
        How to use:
            Pass bytes to the message handler using the receive_bytes method.
            Figure out if the handler is done parsing the message or needs more bytes using the is_done_obtaining_values method.
            Get the parsed values as a dictionary using the get_values method.
            Get the parsed type code using get_protocol_type_code.
            Get the number of bytes that were extracted as part of the message using the get_number_of_bytes_extracted method.
            Tell it to prepare for the next message using the prepare_for_next_message method after you extract these values.
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

    def _update_values_based_on_fieldless_protocol(self):
        self.values = {}
        self.is_done = True

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
        if self.protocol.get_number_of_fields() == 0:
            self._update_values_based_on_fieldless_protocol()
        elif self.protocol.is_fixed_length():
            self._update_values_based_on_fixed_length_protocol()
        else:
            self._update_values_based_on_variable_length_protocol()

    def receive_bytes(self, input_bytes):
        if self.protocol:
            self._update_bytes(input_bytes)
            self._update_values()
        elif len(input_bytes) >= TYPE_CODE_SIZE:
            self._update_protocol(input_bytes)
            remaining_bytes = compute_message_after_type_code(input_bytes)
            self.receive_bytes(remaining_bytes)

    def _update_protocol(self, input_bytes):
        type_code = unpack_type_code_from_message(input_bytes)
        protocol = self.protocol_map.get_protocol_with_type_code(type_code)
        self._initialize(protocol)

    def is_done_obtaining_values(self):
        return self.is_done

    def get_protocol(self):
        return self.protocol
    
    def get_protocol_type_code(self):
        return self.protocol.get_type_code()

    def prepare_for_next_message(self):
        self.protocol = None
        self.is_done = False

    def get_values(self):
        return self.values
    
    def get_number_of_bytes_extracted(self):
        return self.bytes_index

class ProtocolCallbackHandler:
    """Used to map between the callback functions to be called when a message corresponding to a protocol is received"""
    def __init__(self):
        self.callbacks = {}
    
    def register_callback_with_protocol(self, callback, protocol_type_code):
        """
            Registers a callback with a type code
            callback: a callback function that receives values corresponding to a message in the protocol in a dictionary
            mapping field names to values
            protocol_type_code: the type code for the corresponding protocol
        """
        self.callbacks[protocol_type_code] = callback
    
    def pass_values_to_protocol_callback_with_connection_information(self, values, protocol_type_code, connection_information):
        """
            Calls the specified callback with the corresponding values and connection information
            values: a dictionary mapping field names to values
            protocol_type_code: the type code for the corresponding protocol
            connection_information: information used to identify the connection involved in the message
        """
        return self.callbacks[protocol_type_code](values, connection_information)

    def pass_values_to_protocol_callback(self, values, protocol_type_code):
        """
            Calls the specified callback with the corresponding values
            values: a dictionary mapping field names to values
            protocol_type_code: the type code for the corresponding protocol
        """
        return self.callbacks[protocol_type_code](values)

    def has_protocol(self, protocol_type_code):
        """
            Returns true if there is a callback in the handler corresponding to the protocol type code
            and false otherwise
            protocol_type_code: the type code for the corresponding protocol
        """
        return protocol_type_code in self.callbacks

def is_any_field_variable_length(fields):
    """Returns true if any of the fields passed to it are fixed length"""
    for field in fields:
        if not field.is_fixed_length():
            return True
    return False

def create_protocol_with_fields(type_code: int, fields = None):
    """
        Returns a MessageProtocol object with the specified type code and fields
        type_code: an integer number used to distinguish between different message protocols.
        fields: a list of protocol fields
    """
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
    """
        Returns a message protocol with the specified type code for messages having a single variable length string field
    """
    field = create_string_protocol_field("text", 2)
    protocol = create_protocol(type_code, field)
    return protocol

def create_single_byte_nonnegative_integer_message_protocol(type_code: int):
    """
        Returns a message protocol with the specified type code for messages having a single nonnegative single byte integer field
    """
    field = create_single_byte_nonnegative_integer_protocol_field('number')
    protocol = create_protocol(type_code, field)
    return protocol