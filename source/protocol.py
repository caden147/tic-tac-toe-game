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
        """Gives the text used to represent the field in a struct.pack or struck.unpack call"""
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
    def __init__(self, name: str, struct_text: str, max_size: int = 1):
        self.name = name
        self.struct_text = struct_text
        self.max_size = max_size
    
    def get_name(self):
        return self.name
    
    def compute_struct_text(self):
        return self.struct_text

    def get_max_size(self):
        return self.max_size
    
    def is_fixed_length(self):
        return False

class MessageProtocol:
    def get_type_code(self):
        pass

    def pack(self, *args):
        pass

    def is_fixed_length(self):
        return True

class FixedLengthMessageProtocol(MessageProtocol):
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields

    def compute_fields_string(self):
        text = ">"
        for field in self.fields:
            text += field.compute_struct_text()
        return text

    def pack(self, *args):
        type_code_bytes = pack_type_code(self.type_code)
        values_bytes = struct.pack(self.compute_fields_string(), *args)
        return type_code_bytes + values_bytes

    def unpack(self, input_bytes):
        results = {}
        values = struct.unpack(self.compute_fields_string(), input_bytes)
        for i in range(len(values)):
            name = self.fields[i].get_name()
            results[name] = values[i]
        return results

    def get_type_code(self):
        return self.type_code
    
    def compute_size(self):
        """Returns the size in bytes of a message using the protocol"""
        size = 0
        for i in range(len(self.fields)):
            size += self.fields[i].get_size()
        return size

class VariableLengthMessageProtocol(MessageProtocol):
    def __init__(self, type_code, fields):
        self.type_code = type_code
        self.fields = fields
    
    def get_type_code(self):
        return self.type_code
    
    def pack(self, *args):
        values_bytes = pack_type_code(self.type_code)
        for index, field in enumerate(self.fields):
            field_bytes = struct.pack(">" + field.compute_struct_text(), args[index])[0]
            if not field.is_fixed_length():
                size_bytes = struct.pack(">" + compute_format_representation_for_size(field.get_max_size()), len(field_bytes))
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
        return struct.unpack(">" + field.compute_struct_text(), relevant_bytes)[0]
    
    def unpack_fixed_length_field(self, i, input_bytes, starting_index):
        field = self.fields[i]
        length = self.compute_fixed_length_field_length(i)
        relevant_bytes = input_bytes[starting_index: starting_index + length]
        return struct.unpack(">" + field.compute_struct_text(), relevant_bytes)[0]

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
    
